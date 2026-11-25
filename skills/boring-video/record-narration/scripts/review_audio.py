#!/usr/bin/env python3
"""Build an audio-review ledger and check recorded evidence, never listen or cut audio."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import wave

CHECKS = ['sentence_restart', 'short_repeat', 'partial_word_restart',
          'self_correction', 'mixed_language', 'proper_name']
AUDIO_METHODS = {'human_listening', 'audio_model'}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def binding(path):
    path = Path(path).resolve()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return {'path': str(path), 'sha256': digest.hexdigest()}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def interval(item, duration, allow_point=False):
    a, b = item['start'], item['end']
    if not (number(a) and number(b) and 0 <= a <= b <= duration and (allow_point or a < b)):
        raise ValueError(f'Invalid interval: {item}')
    return a, b


def gaps(ranges, duration):
    cursor, missing = 0., []
    for start, end in sorted(ranges):
        if start > cursor:
            missing.append([cursor, start])
        cursor = max(cursor, end)
    if cursor < duration:
        missing.append([cursor, duration])
    return missing


def candidates(data, duration):
    """Heuristic hints only; recall is unmeasured. Token spans are not syllable boundaries."""
    words = data.get('words', [])
    found = []
    for i, word in enumerate(words):
        start, end = interval(word, duration, allow_point=True)
        text = word['word'].strip()
        previous = words[i - 1]['word'].strip() if i else ''
        reasons = []
        if end - start >= max(1.2, len(text) * .4):
            reasons.append('long_word_span')
        probability = word.get('probability')
        if number(probability) and probability < .6:
            reasons.append('low_confidence')
        if text and previous and text == previous:
            reasons.append('adjacent_repeat')
        if (text and previous and re.search('[A-Za-z]', text + previous)
                and re.search('[\u4e00-\u9fff]', text + previous)):
            reasons.append('mixed_language')
        if reasons:
            found.append({'id': f'word-{i}', 'start': start, 'end': end,
                          'context_start': max(0., start - 3),
                          'context_end': min(duration, end + 3), 'text': text,
                          'reasons': reasons, 'decision': 'pending', 'evidence': ''})
    return found


def map_span(start, end, kept):
    """Map retained speech; a fully removed interval maps to its output seam."""
    spans = [(k['output_start'] + max(start, k['source_start']) - k['source_start'],
              k['output_start'] + min(end, k['source_end']) - k['source_start'])
             for k in kept if max(start, k['source_start']) < min(end, k['source_end'])]
    if spans:
        return spans[0][0], spans[-1][1], False
    for k in kept:
        if start < k['source_start']:
            return k['output_start'], k['output_start'], True
        if start < k['source_end'] or start == end == k['source_end']:
            point = k['output_start'] + start - k['source_start']
            return point, point, False
    point = kept[-1]['output_end']
    return point, point, True


def inherit(prior, kept, duration):
    result = {'candidates': [], 'user_reports': []}
    for collection in result:
        for item in prior[collection]:
            a, b = interval(item, prior['duration'], allow_point=True)
            ca = item.get('context_start', max(0, a - 3))
            cb = item.get('context_end', min(prior['duration'], b + 3))
            interval({'start': ca, 'end': cb}, prior['duration'])
            start, end, removed = map_span(a, b, kept)
            left, right, _ = map_span(ca, cb, kept)
            # Edit reports accumulate floating-point durations; clip rounding at file bounds.
            start, end, left, right = [min(duration, max(0., t)) for t in (start, end, left, right)]
            result[collection].append({
                'id': f'prior:{collection}:{item["id"]}',
                'origin': {'collection': collection, 'id': item['id']},
                'source_start': a, 'source_end': b, 'removed_by_edit': removed,
                'text': item.get('text', ''), 'description': item.get('description', ''),
                'start': start, 'end': end,
                'context_start': min(left, max(0., start - 3)),
                'context_end': max(right, min(duration, end + 3)),
                'decision': 'pending', 'evidence': ''})
    return result


def validate_map(edit, prior, duration):
    if (Path(edit['source']).resolve() != Path(prior['audio']['path']).resolve()
            or edit['source_sha256'] != prior['audio']['sha256']
            or edit['duration_before'] != prior['duration']):
        raise ValueError('Previous review must bind the edit source')
    cursor, output = 0., 0.
    for k in edit['kept']:
        a, b = interval({'start': k['source_start'], 'end': k['source_end']}, prior['duration'])
        if (a < cursor or k['output_start'] != output
                or not number(k['output_end'])
                or abs(k['output_end'] - output - (b - a)) > .0001):
            raise ValueError('Invalid source-to-output edit map')
        cursor, output = b, k['output_end']
    if not edit['kept'] or abs(output - duration) > .0001:
        raise ValueError('Edit map duration mismatch')


def create(audio, transcript, edit_report=None, previous_review=None, _depth=0):
    with wave.open(str(audio), 'rb') as stream:
        duration = stream.getnframes() / stream.getframerate()
    if not number(duration) or duration <= 0:
        raise ValueError('Audio must have positive duration')
    data = load(transcript)
    if Path(data['audio']).resolve() != Path(audio).resolve():
        raise ValueError('Transcript must name this audio')
    if _depth > 100:
        raise ValueError('Review lineage cycle or excessive depth')
    prior = load(previous_review) if previous_review else None
    if prior is not None:
        assess(prior, _depth + 1)  # Pending work may carry forward; corrupt provenance may not.
    joins, inherited = [], {'candidates': [], 'user_reports': []}
    if edit_report:
        if prior is None:
            raise ValueError('Edited audio requires --previous-review for the source ledger')
        edit = load(edit_report)
        if (Path(edit['audio']).resolve() != Path(audio).resolve()
                or abs(edit['duration_after'] - duration) > .0001):
            raise ValueError('Edit report must describe this final audio')
        validate_map(edit, prior, duration)
        inherited = inherit(prior, edit['kept'], duration)
        joins = [item['output_start'] for item in edit['kept'][1:]]
    elif prior is not None:
        if binding(audio) != prior['audio']:
            raise ValueError('A changed audio version requires its edit report')
        inherited = inherit(prior, [dict(source_start=0., source_end=duration,
                                        output_start=0., output_end=duration)], duration)
    boundaries = [dict(id=name, start=max(0., t - 3), end=min(duration, t + 3), evidence='')
                  for name, t in [('opening', 0.), ('ending', duration)]
                  + [(f'join-{i}', t) for i, t in enumerate(joins)]]
    if prior is not None and not edit_report:
        boundaries = [dict(b, evidence='') for b in prior['boundary_checks']]
    return {'version': 2, 'audio': binding(audio), 'transcript': binding(transcript),
            'edit_report': binding(edit_report) if edit_report else None,
            'previous_review': binding(previous_review) if previous_review else None,
            'duration': duration, 'timebase': 'bound audio seconds',
            'capabilities': [], 'asr_runs': [], 'coverage': [],
            'candidates': candidates(data, duration) + inherited['candidates'],
            'user_reports': inherited['user_reports'],
            'boundary_checks': boundaries,
            'limitations': []}


def assess(report, _depth=0):
    """Validate declarations against bound artifacts; cannot authenticate listening."""
    if report['version'] not in (1, 2) or report['timebase'] != 'bound audio seconds':
        raise ValueError('Unsupported review schema/timebase')
    for key in ('audio', 'transcript', 'edit_report', 'previous_review'):
        item = report.get(key)
        if item and binding(item['path']) != item:
            raise ValueError(f'{key} changed; create a new review')
    baseline = create(report['audio']['path'], report['transcript']['path'],
                      report['edit_report']['path'] if report['edit_report'] else None,
                      report['previous_review']['path'] if report.get('previous_review') else None, _depth)
    duration = baseline['duration']
    if report['duration'] != duration:
        raise ValueError('Duration differs from bound audio')
    issues, covered = [], []
    capabilities = {c['id']: c for c in report['capabilities']}
    for record in report['coverage']:
        span = interval(record, duration)
        capability = capabilities.get(record['capability'], {})
        if (capability.get('kind') in AUDIO_METHODS and capability.get('available') is True
                and capability.get('probe_evidence') and capability.get('tool')
                and record.get('evidence') and set(CHECKS) <= set(record.get('checks', []))):
            covered.append(span)
        else:
            issues.append(f'Non-listening or incomplete coverage record: {span}')
    missing = gaps(covered, duration)
    if missing:
        issues.append('Full spoken-audio review incomplete')

    def reviewed(a, b):
        return not any(x < b and y > a for x, y in missing)

    coverage_issues = len(issues)
    for collection in ('candidates', 'user_reports'):
        actual = {c['id']: c for c in report[collection]}
        if len(actual) != len(report[collection]):
            raise ValueError(f'Duplicate IDs in {collection}')
        for expected in baseline[collection]:
            item = actual.get(expected['id'], {})
            immutable = set(expected) - {'context_start', 'context_end', 'decision', 'evidence'}
            if any(item.get(k) != expected[k] for k in immutable):
                raise ValueError(f'Missing or altered candidate/report: {expected["id"]}')
            if (item.get('context_start', float('inf')) > expected['context_start']
                    or item.get('context_end', -1) < expected['context_end']):
                raise ValueError(f'Candidate context may expand, not shrink: {expected["id"]}')
    removed = {(collection, c['id']) for collection in ('candidates', 'user_reports')
               for c in baseline[collection] if c.get('removed_by_edit')}
    for collection, item in [(name, c) for name in ('candidates', 'user_reports') for c in report[name]]:
        a, b = interval(item, duration, allow_point=True)
        ca, cb = item.get('context_start', a), item.get('context_end', b)
        interval({'start': ca, 'end': cb}, duration)
        if ca > max(0, a - 3) or cb < min(duration, b + 3):
            issues.append(f'Insufficient surrounding speech: {item["id"]}')
        allowed = {'removed'} if (collection, item['id']) in removed else {'keep'}
        if (item.get('decision') not in allowed
                or not item.get('evidence') or not reviewed(ca, cb)):
            issues.append(f'Unresolved candidate/report: {item["id"]}')
        # A removed item belongs to another audio version; this ledger cannot certify it.
        if item.get('decision') == 'removed_in_new_version':
            issues.append(f'Review the new final audio: {item["id"]}')
    candidate_issues = len(issues) - coverage_issues
    boundaries = {c['id']: c for c in report['boundary_checks']}
    for expected in baseline['boundary_checks']:
        item = boundaries.get(expected['id'], {})
        if any(item.get(k) != expected[k] for k in ('start', 'end')):
            raise ValueError(f'Missing or altered boundary: {expected["id"]}')
        if not item.get('evidence') or not reviewed(expected['start'], expected['end']):
            issues.append(f'Boundary unchecked: {expected["id"]}')
    boundary_issues = len(issues) - coverage_issues - candidate_issues
    runs = report['asr_runs']
    warnings = []
    identities = [(r.get('engine'), r.get('model')) for r in runs]
    if len(set(identities)) < len(identities):
        warnings.append('Repeated engine/model is correlated ASR, not independent listening')
    if runs:
        warnings.append('ASR runs do not contribute spoken-audio coverage')
    return {'status': 'reviewed' if not issues else 'incomplete',
            'gates': {'candidate_decisions': 'incomplete' if candidate_issues else 'recorded',
                      'boundary_review': 'incomplete' if boundary_issues else 'recorded',
                      'spoken_audio_review': 'incomplete' if coverage_issues else 'recorded'},
            'duration': duration, 'spoken_audio_gaps': missing,
            'issues': issues, 'warnings': warnings,
            'limit': 'Checks declared evidence and coverage only; does not verify that listening occurred or guarantee detection.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Create candidate hints and an empty review ledger')
    init.add_argument('--audio', type=Path, required=True)
    init.add_argument('--transcript', type=Path, required=True)
    init.add_argument('--edit-report', type=Path)
    init.add_argument('--previous-review', type=Path, help='Source ledger; required with --edit-report')
    init.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('check', help='Print coverage gaps; exit 2 when incomplete')
    check.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'init':
            report = create(args.audio, args.transcript, args.edit_report, args.previous_review)
            with args.output.open('x', encoding='utf-8') as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
            print(args.output)
            return 0
        result = assess(load(args.review))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] == 'reviewed' else 2
    except (OSError, ValueError, KeyError, TypeError, wave.Error) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
