from tools.calculate_pv_output import pv_output

if __name__ == "__main__":
    # Test manuale
    risultato = pv_output(
        latitude=41.9,
        longitude=12.5,
        efficiency=0.75,
        azimuth=0,
        slope=30,
        module_power=3.0
    )
    print(risultato)