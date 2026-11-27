import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

class ComparisonTests(unittest.TestCase):
    def test_mapping_refuses_deleted_source_time(self):
        from compare_audio_edits import map_time
        r={'kept':[{'source_start':0.,'source_end':1.,'output_start':0.},
                   {'source_start':2.,'source_end':4.,'output_start':1.}]}
        self.assertEqual(map_time(3.,r),2.)
        with self.assertRaises(ValueError):map_time(1.5,r)

    def test_retained_interior_check_detects_changed_samples(self):
        from compare_audio_edits import interior_identity
        import numpy as np
        source=np.zeros(48000,dtype=np.int16);out=source.copy();out[1000]=1
        report={'kept':[{'source_start':0.,'source_end':1.,'output_start':0.}]}
        check=interior_identity(source,out,report,48000)
        self.assertEqual(check['mismatched_samples'],1)

if __name__=='__main__':unittest.main()
