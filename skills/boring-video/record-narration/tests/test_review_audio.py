"""Synthetic failure cases: no private recordings or claimed audio understanding."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/review_audio.py'
spec = importlib.util.spec_from_file_location('review_audio', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audio = self.root / 'test.wav'
        with wave.open(str(self.audio), 'wb') as stream:
            stream.setparams((1, 2, 100, 0, 'NONE', 'not compressed'))
            stream.writeframes(b'\0\0' * 2000)
        self.transcript = self.root / 'raw.json'
        # Fluent ASR omits a reported repeat. Abnormal C is a hint, not a boundary.
        self.data = {'audio': str(self.audio), 'model': 'small', 'words': [
            {'word': '内置', 'start': 8.41, 'end': 9.11, 'probability': .9},
            {'word': 'C', 'start': 9.11, 'end': 10.77, 'probability': .443},
            {'word': 'Provider', 'start': 10.77, 'end': 11.3, 'probability': .9}]}
        self.transcript.write_text(json.dumps(self.data))
        self.report = r.create(self.audio, self.transcript)

    def complete(self):
        report = copy.deepcopy(self.report)
        report['capabilities'] = [{'id': 'listener', 'kind': 'human_listening',
            'available': True, 'tool': 'synthetic test declaration', 'probe_evidence': 'fixture only'}]
        report['coverage'] = [{'start': 0, 'end': 20, 'capability': 'listener',
            'checks': list(r.CHECKS), 'evidence': 'synthetic evidence, not actual listening'}]
        for c in report['candidates']:
            c.update(decision='keep', evidence='synthetic supported keep')
        for b in report['boundary_checks']:
            b['evidence'] = 'synthetic boundary check'
        return report

    def test_fluent_asr_still_flags_long_low_confidence_mixed_language(self):
        c = next(c for c in self.report['candidates'] if c['text'] == 'C')
        self.assertTrue({'long_word_span', 'low_confidence', 'mixed_language'} <= set(c['reasons']))
        self.assertEqual(c['decision'], 'pending')
        self.assertEqual(r.assess(self.report)['spoken_audio_gaps'], [[0., 20.]])

    def test_same_model_rerun_never_counts_as_listening(self):
        report = self.complete()
        report['capabilities'][0]['kind'] = 'asr'
        report['asr_runs'] = [{'engine': 'faster-whisper', 'model': 'small'}] * 2
        result = r.assess(report)
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(result['spoken_audio_gaps'], [[0., 20.]])
        self.assertIn('correlated', result['warnings'][0])
        self.assertEqual(result['gates']['spoken_audio_review'], 'incomplete')

    def test_signal_or_text_checks_cannot_close_coverage(self):
        for method in ('waveform', 'silencedetect', 'pcm_continuity', 'text_review'):
            report = self.complete()
            report['capabilities'][0]['kind'] = method
            self.assertEqual(r.assess(report)['status'], 'incomplete')

    def test_overlap_does_not_hide_unreviewed_gap(self):
        report = self.complete()
        record = report['coverage'][0]
        report['coverage'] = [dict(record, start=0, end=8), dict(record, start=4, end=9),
                              dict(record, start=10, end=20)]
        self.assertEqual(r.assess(report)['spoken_audio_gaps'], [[9, 10]])

    def test_user_report_requires_surrounding_audio_despite_clean_asr(self):
        report = self.complete()
        issue = {'id': 'user-1', 'start': 9, 'end': 10, 'context_start': 6,
                 'context_end': 13, 'decision': 'pending', 'evidence': 'ASR has no repeat'}
        report['user_reports'] = [issue]
        self.assertEqual(r.assess(report)['status'], 'incomplete')
        issue.update(decision='keep', evidence='supported local audio decision')
        self.assertEqual(r.assess(report)['status'], 'reviewed')
        issue['context_start'] = 9
        self.assertEqual(r.assess(report)['status'], 'incomplete')

    def test_missing_hint_or_stale_audio_rejected(self):
        report = self.complete()
        report['candidates'] = []
        with self.assertRaises(ValueError):
            r.assess(report)
        self.audio.write_bytes(self.audio.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            r.assess(self.complete())

    def test_boundary_and_required_checks_gate_completion(self):
        report = self.complete()
        self.assertEqual(r.assess(report)['status'], 'reviewed')
        report['boundary_checks'][0]['evidence'] = ''
        self.assertEqual(r.assess(report)['status'], 'incomplete')
        report = self.complete()
        report['coverage'][0]['checks'].remove('short_repeat')
        self.assertEqual(r.assess(report)['status'], 'incomplete')

    def edited_fixture(self, cuts=((2, 4),)):
        previous = self.root / 'source-review.json'
        source = self.complete()
        source['user_reports'] = [{'id': 'user-repeat', 'start': 9, 'end': 10,
            'context_start': 6, 'context_end': 13, 'description': 'reported repeat',
            'decision': 'pending', 'evidence': ''}]
        source['candidates'].append({'id': 'manual-restart', 'start': 2.5, 'end': 3,
            'context_start': 0, 'context_end': 6, 'decision': 'pending', 'evidence': ''})
        previous.write_text(json.dumps(source))
        kept, cursor, out = [], 0, 0
        for a, b in list(cuts) + [(20, 20)]:
            if a > cursor:
                kept.append(dict(source_start=cursor, source_end=a,
                    output_start=out, output_end=out + a - cursor))
                out += a - cursor
            cursor = b
        audio = self.root / 'edited.wav'
        with wave.open(str(audio), 'wb') as stream:
            stream.setparams((1, 2, 100, 0, 'NONE', 'not compressed'))
            stream.writeframes(b'\0\0' * int(out * 100))
        transcript = self.root / 'final.json'
        transcript.write_text(json.dumps({'audio': str(audio), 'words': []}))
        edit = self.root / 'edit-report.json'
        edit.write_text(json.dumps({'audio': str(audio), 'source': str(self.audio),
            'source_sha256': r.binding(self.audio)['sha256'], 'duration_before': 20,
            'duration_after': out, 'kept': kept}))
        return audio, transcript, edit, previous

    def fill_listening(self, report):
        template = self.complete()
        report['capabilities'] = template['capabilities']
        report['coverage'] = [dict(template['coverage'][0], end=report['duration'])]
        for b in report['boundary_checks']:
            b['evidence'] = 'synthetic boundary finding'
        return report

    def test_edit_map_requires_previous_review_and_every_join(self):
        audio, transcript, edit, previous = self.edited_fixture()
        with self.assertRaises(ValueError):
            r.create(audio, transcript, edit)
        report = r.create(audio, transcript, edit, previous)
        self.assertEqual(report['boundary_checks'][-1]['id'], 'join-0')
        report['boundary_checks'].pop()
        with self.assertRaises(ValueError):
            r.assess(report)

    def test_prior_reports_and_manual_candidates_cannot_disappear(self):
        audio, transcript, edit, previous = self.edited_fixture()
        report = self.fill_listening(r.create(audio, transcript, edit, previous))
        user = report['user_reports'][0]
        self.assertEqual((user['start'], user['end']), (7, 8))
        self.assertEqual(user['decision'], 'pending')
        self.assertEqual(r.assess(report)['status'], 'incomplete')
        dropped = copy.deepcopy(report)
        dropped['user_reports'] = []
        with self.assertRaises(ValueError):
            r.assess(dropped)
        manual = next(c for c in report['candidates'] if c['origin']['id'] == 'manual-restart')
        self.assertTrue(manual['removed_by_edit'])
        self.assertEqual(manual['start'], manual['end'])
        for c in report['candidates'] + report['user_reports']:
            c.update(decision='removed' if c['removed_by_edit'] else 'keep',
                     evidence='synthetic local final-audio disposition')
        self.assertEqual(r.assess(report)['status'], 'reviewed')
        dropped = copy.deepcopy(report)
        dropped['candidates'] = []
        with self.assertRaises(ValueError):
            r.assess(dropped)
        user['decision'] = 'removed'
        self.assertEqual(r.assess(report)['status'], 'incomplete')

    def test_prior_review_binding_and_edit_source_must_match(self):
        audio, transcript, edit, previous = self.edited_fixture()
        report = r.create(audio, transcript, edit, previous)
        previous.write_text(previous.read_text() + ' ')
        with self.assertRaises(ValueError):
            r.assess(report)
        data = json.loads(edit.read_text())
        data['source_sha256'] = 'wrong-source'
        edit.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            r.create(audio, transcript, edit, previous)

    def test_context_can_expand_but_word_span_cannot_change(self):
        report = self.complete()
        report['candidates'][0].update(context_start=0, context_end=20)
        self.assertEqual(r.assess(report)['status'], 'reviewed')
        report['coverage'][0]['start'] = 1
        result = r.assess(report)
        self.assertTrue(any('Unresolved candidate' in i for i in result['issues']))
        report = self.complete()
        report['candidates'][0]['start'] -= .1
        with self.assertRaises(ValueError):
            r.assess(report)

    def test_fresh_review_of_same_audio_preserves_reports_and_join_checks(self):
        audio, transcript, edit, previous = self.edited_fixture()
        final = r.create(audio, transcript, edit, previous)
        final_path = self.root / 'final-review.json'
        final_path.write_text(json.dumps(final))
        fresh = r.create(audio, transcript, previous_review=final_path)
        self.assertEqual(fresh['boundary_checks'], final['boundary_checks'])
        self.assertEqual(len(fresh['user_reports']), 1)
        self.assertEqual(r.assess(fresh)['status'], 'incomplete')

    def test_partial_head_tail_and_multiple_cut_mapping(self):
        kept = [dict(source_start=2, source_end=4, output_start=0, output_end=2),
                dict(source_start=6, source_end=10, output_start=2, output_end=6)]
        for span, expected in [((0, 1), (0, 0, True)), ((3, 7), (1, 3, False)),
                               ((4.5, 5), (2, 2, True)), ((11, 12), (6, 6, True)),
                               ((10, 10), (6, 6, False))]:
            self.assertEqual(r.map_span(*span, kept), expected)

    def test_removed_decision_requires_verified_edit_mapping(self):
        report = self.complete()
        report['candidates'][0].update(removed_by_edit=True, decision='removed')
        self.assertEqual(r.assess(report)['status'], 'incomplete')

    def test_zero_time_word_preserved_as_hint(self):
        self.data['words'][1]['end'] = 9.11
        self.assertIn('low_confidence', next(c for c in r.candidates(self.data, 20) if c['text'] == 'C')['reasons'])

    def test_empty_evidence_unavailable_probe_and_invalid_ranges_fail_closed(self):
        for field, value in [('available', False), ('probe_evidence', '')]:
            report = self.complete()
            report['capabilities'][0][field] = value
            self.assertEqual(r.assess(report)['status'], 'incomplete')
        for start, end in [(float('nan'), 10), (0, float('inf')), (-1, 3), (4, 3), (0, 21)]:
            report = self.complete()
            report['coverage'][0].update(start=start, end=end)
            with self.assertRaises(ValueError):
                r.assess(report)

    def test_cli_incomplete_exit_and_no_overwrite(self):
        path = self.root / 'review.json'
        args = [sys.executable, str(SCRIPT), 'init', '--audio', str(self.audio),
                '--transcript', str(self.transcript), '--output', str(path)]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        before = path.read_bytes()
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)
        self.assertEqual(path.read_bytes(), before)
        result = subprocess.run([sys.executable, str(SCRIPT), 'check', '--review', str(path)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
