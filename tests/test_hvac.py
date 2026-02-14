
from src.calcs_hvac import hvac_predim, ventilation_flow

def test_hvac_predim():
    r = hvac_predim(1000,"Office",50,70,0.8)
    assert r["Q_heat_kW"] > 0
    assert r["Q_cool_kW"] > 0

def test_ventilation():
    v = ventilation_flow(1000,100,"Cat II")
    assert v["q_outdoor_m3h"] > 0
