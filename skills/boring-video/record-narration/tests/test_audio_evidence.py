import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

class AcousticTests(unittest.TestCase):
    def engine(self):
        import audio_evidence
        return audio_evidence

    def signal(self):
        # 0.2..0.8 kept speech, 1..1.5 discarded, 1.55..1.8 missed tail,
        # 2.6..3.2 complete replacement. Quiet room tone, no digital silence.
        x=np.full(48000*4,10,dtype=np.int16)
        for a,b in [(.2,.8),(1,1.5),(1.55,1.8),(2.6,3.2)]:
            n=round((b-a)*48000)
            x[round(a*48000):round(b*48000)]=(5000*np.sin(np.arange(n)*.1)).astype(np.int16)
        return x

    def test_refines_end_past_missed_tail_and_keeps_room_before_replacement(self):
        e=self.engine();r=e.refine_cut(self.signal(),48000,1.,1.5,.7,2.65)
        self.assertEqual(r['status'],'ready')
        self.assertGreater(r['end'],1.8)
        self.assertLess(r['end'],2.6)
        self.assertLessEqual(r['start'],1.)
        self.assertGreater(r['start'],.8)

    def test_no_quiet_boundary_is_not_auto_cut(self):
        e=self.engine();x=(5000*np.sin(np.arange(48000*4)*.1)).astype(np.int16)
        r=e.refine_cut(x,48000,1.,1.5,.7,2.65)
        self.assertEqual(r['status'],'unresolved')

    def test_competing_long_pauses_are_ambiguous(self):
        e=self.engine();x=self.signal()
        x[round(2.1*48000):round(2.3*48000)]=3000
        r=e.refine_cut(x,48000,1.,1.5,.7,2.65)
        self.assertEqual(r['status'],'unresolved')
        self.assertIn('ambiguous',r['reason'])

    def test_zero_duration_alignment_is_not_deliverable(self):
        e=self.engine()
        issues=e.alignment_issues([{'word':'创建','start':1.,'end':1.,'probability':.9}],3.)
        self.assertTrue(issues)

    def test_zero_duration_char_is_retained_in_shared_timed_unit(self):
        e=self.engine()
        words=[{'word':'应','start':1.,'end':1.2}, {'word':'用','start':1.2,'end':1.2},
               {'word':'跑起来','start':1.4,'end':2.}]
        result,notes=e.coalesce_zero_duration(words)
        self.assertEqual(''.join(w['word'] for w in result),'应用跑起来')
        self.assertEqual(result[0]['word'],'应用')
        self.assertEqual((result[0]['start'],result[0]['end']),(1.,1.2))
        self.assertTrue(notes)

    def test_initial_layout_retains_raw_zero_duration_evidence(self):
        import copy
        from process_audio import initial_layout
        data={'words':[{'word':'应','start':.5,'end':1.},
                       {'word':'用','start':1.,'end':1.},
                       {'word':'运行','start':1.2,'end':2.}],
              'segments':[{'id':1,'start':.5,'end':2.,'text':'应用运行'}]}
        before=copy.deepcopy(data)
        initial=initial_layout(data)
        self.assertEqual(data,before)
        self.assertEqual(''.join(x['text'] for x in initial['segments']),'应用运行')
        self.assertTrue(initial['input_timing_notes'])

    def test_dominant_long_pause_beats_tiny_breath_gaps(self):
        e=self.engine();x=np.full(48000*5,10,dtype=np.int16)
        for a,b in [(.2,.8),(1.,1.5),(3.3,3.5),(3.59,3.7),(3.79,4.5)]:
            n=round((b-a)*48000)
            x[round(a*48000):round(b*48000)]=(5000*np.sin(np.arange(n)*.1)).astype(np.int16)
        r=e.refine_cut(x,48000,1.,1.5,.7,3.82)
        self.assertEqual(r['status'],'ready')
        self.assertGreater(r['end'],1.8)
        self.assertLess(r['end'],3.3)

    def test_initial_layout_failure_is_recorded_without_repeating_recognition(self):
        import tempfile,json
        from pathlib import Path
        from process_audio import export_initial
        data={'words':[{'word':'SessionRequestPermission','start':.5,'end':2.}],
              'segments':[{'id':1,'start':.5,'end':2.,'text':'SessionRequestPermission'}]}
        with tempfile.TemporaryDirectory() as tmp:
            result=export_initial(data,Path(tmp))
            self.assertIsNone(result)
            status=json.loads((Path(tmp)/'initial-layout-status.json').read_text())
            self.assertEqual(status['status'],'needs_alignment_or_layout_review')
            self.assertFalse((Path(tmp)/'subtitles.initial.srt').exists())

if __name__=='__main__':unittest.main()
