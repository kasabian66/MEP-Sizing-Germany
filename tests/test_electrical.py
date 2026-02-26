
from src.calcs_electrical import LoadItem, compute_demand, size_feeder

def test_compute_demand():
    loads=[LoadItem("A",10,0.5),LoadItem("B",5,1.0)]
    p,df=compute_demand(loads)
    assert abs(p-10.0) < 1e-6
    assert len(df)==2

def test_size_feeder():
    res = size_feeder(p_dem_kw=50, length_m=30, max_vdrop_pct=3.0)
    assert res["Section_mm2"] > 0
    assert res["I_design_A"] > 0
