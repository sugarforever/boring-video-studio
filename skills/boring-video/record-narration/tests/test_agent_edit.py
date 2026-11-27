import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

class AgentEditTests(unittest.TestCase):
    def setUp(self):
        import agent_edit
        self.m = agent_edit
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audio = self.root/'source.wav'
        with wave.open(str(self.audio), 'wb') as f:
            f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            f.writeframes(b'\0\0' * 48000 * 5)
        self.tx = self.root/'transcript.json'
        self.tx.write_text(json.dumps({'words': [
            {'word':'看看','start':.5,'end':1.}, {'word':'工具','start':1.,'end':1.5},
            {'word':'看看','start':2.,'end':2.5}, {'word':'工具','start':2.5,'end':3.},
            {'word':'怎样使用','start':3.,'end':4.}]}))
        self.script = self.root/'script.txt'; self.script.write_text('看看工具怎样使用')
        self.bundle = self.m.prepare(self.audio, self.tx, self.script, self.root/'review')

    def apply_word(self, *args):
        return self.m.apply(*args, boundary_mode='word')

    def test_unsafe_acoustic_cut_remains_unapplied(self):
        r=self.m.apply(self.root/'review',self.plan(),self.root/'result')
        self.assertEqual(len(r['words']),5)
        report=json.loads((self.root/'result/boundary-report.json').read_text())
        self.assertEqual(report[0]['status'],'unresolved')
        self.assertEqual(r['status'],'draft_review_required')

    def plan(self):
        return {'bundle_id':self.bundle['bundle_id'], 'corrections':[], 'cuts':[
            {'first':'w000000','last':'w000001','replacement_first':'w000002',
             'replacement_last':'w000004','reason':'废弃开头，后面完整重说'}]}

    def test_apply_preserves_original_and_maps_words(self):
        before = self.audio.read_bytes()
        result = self.apply_word(self.root/'review', self.plan(), self.root/'result')
        self.assertEqual(self.audio.read_bytes(), before)
        self.assertEqual([w['id'] for w in result['words']], ['w000002','w000003','w000004'])
        self.assertAlmostEqual(result['words'][0]['start'], 1.)
        self.assertEqual(result['status'], 'draft_review_required')
        with wave.open(str(self.root/'result/narration.edited.wav')) as f:
            self.assertEqual(f.getnframes(), 4*48000)
        self.assertIn('看看工具怎样使用', (self.root/'result/subtitles.draft.srt').read_text())
        self.assertTrue((self.root/'result/review.html').exists())

    def test_stale_audio_and_transcript_rejected(self):
        self.tx.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'changed'): self.apply_word(self.root/'review',self.plan(),self.root/'result')
        self.assertFalse((self.root/'result').exists())

    def test_wrong_bundle_rejected(self):
        p=self.plan();p['bundle_id']='wrong'
        with self.assertRaises(ValueError): self.apply_word(self.root/'review',p,self.root/'result')

    def test_replacement_cannot_be_deleted_by_another_cut(self):
        p=self.plan();p['cuts'].append({'first':'w000002','last':'w000004',
          'replacement_first':'w000000','replacement_last':'w000001','reason':'bad'})
        with self.assertRaisesRegex(ValueError,'replacement'): self.apply_word(self.root/'review',p,self.root/'result')

    def test_correction_preserves_raw_evidence(self):
        p=self.plan();p['corrections']=[{'id':'w000004','text':'如何使用','reason':'识别校正'}]
        result=self.apply_word(self.root/'review',p,self.root/'result')
        self.assertEqual(result['words'][-1]['raw_text'],'怎样使用')
        self.assertEqual(result['words'][-1]['text'],'如何使用')

    def test_audio_changes_invalidate_decisions(self):
        with self.audio.open('ab') as f: f.write(b'x')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply_word(self.root/'review', self.plan(), self.root/'result')

    def test_no_cuts_preserves_all_words(self):
        p=self.plan();p['cuts']=[]
        result=self.apply_word(self.root/'review',p,self.root/'result')
        self.assertEqual(len(result['words']),5)
        self.assertEqual(result['words'][0]['start'],.5)

    def test_overlapping_cuts_rejected_before_export(self):
        p=self.plan();p['cuts'].append(dict(p['cuts'][0]))
        with self.assertRaisesRegex(ValueError,'nonoverlapping'):
            self.apply_word(self.root/'review',p,self.root/'result')
        self.assertFalse((self.root/'result').exists())

    def test_long_gaps_are_exported_for_omitted_speech_inspection(self):
        data={'words':[{'word':'前句','start':.1,'end':.5},
                       {'word':'创建和发送以后','start':3.,'end':4.}]}
        self.tx.write_text(json.dumps(data))
        self.m.prepare(self.audio,self.tx,self.script,self.root/'gaps')
        hints=json.loads((self.root/'gaps/inspection-hints.json').read_text())
        self.assertTrue(any(h['kind']=='long_gap' and h['start']==.5 and h['end']==3. for h in hints))

    def test_swarm_recovered_restart_is_removed_without_losing_replacement(self):
        tx={'words':[{'word':text,'start':start,'end':end} for text,start,end in [
            ('创建',125.,127.32),('创建',129.1,129.9),('和发送以后',129.9,131.08)]]}
        # Use the real missed-restart time layout in a silent, synthetic source.
        with wave.open(str(self.audio),'wb') as f:
            f.setparams((1,2,48000,0,'NONE','not compressed'))
            f.writeframes(b'\0\0'*48000*133)
        self.tx.write_text(json.dumps(tx))
        b=self.m.prepare(self.audio,self.tx,self.script,self.root/'recovered')
        p={'bundle_id':b['bundle_id'],'corrections':[],'cuts':[{
           'first':'w000000','last':'w000000','replacement_first':'w000001',
           'replacement_last':'w000002','reason':'recovered abandoned 创建'}]}
        r=self.apply_word(self.root/'recovered',p,self.root/'result')
        self.assertEqual(''.join(w['text'] for w in r['words']),'创建和发送以后')
        self.assertAlmostEqual(r['words'][0]['start'],126.78)
        self.assertEqual(r['words'][0]['raw_text'],'创建')

if __name__=='__main__':unittest.main()
