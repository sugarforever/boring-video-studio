import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

class ReviewPipelineTests(unittest.TestCase):
    def test_gap_inspection_separates_two_attempts(self):
        import narration_review as r
        x=np.full(48000*8,10,dtype=np.int16)
        for a,b in [(2,2.8),(5,6.2)]:
            n=round((b-a)*48000);x[round(a*48000):round(b*48000)]=(4000*np.sin(np.arange(n)*.1)).astype(np.int16)
        windows=r.inspection_windows(x,48000,[{'kind':'long_gap','start':1.,'end':6.5}])
        self.assertEqual(len(windows),2)
        self.assertLess(windows[0]['end'],windows[1]['start'])

    def test_alignment_groups_cover_all_text_with_bounded_windows(self):
        import narration_review as r
        words=[{'text':str(i),'start':float(i),'end':i+.8} for i in range(60)]
        groups=r.alignment_groups(words,61.)
        self.assertEqual(''.join(g['text'] for g in groups),''.join(w['text'] for w in words))
        self.assertTrue(all(g['end']-g['start']<=25 for g in groups))
        self.assertTrue(all(a['end']<=b['start'] for a,b in zip(groups,groups[1:])))

    def test_long_technical_term_blocks_subtitle_layout_without_losing_alignment(self):
        import narration_review as r
        words=[{'word':'SessionRequestPermission','start':.5,'end':2.}]
        result=r.layout_alignment(words,3.)
        self.assertFalse(result['subtitle_exported'])
        self.assertIn('layout_error',result)
        self.assertEqual(words[0]['word'],'SessionRequestPermission')

if __name__=='__main__':unittest.main()
