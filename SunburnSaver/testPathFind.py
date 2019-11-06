from frontend import Start


def test():
    session = Start()

    SUN_WEIGHT = 2

    a = "37.8668556"
    b = "-122.2516966"

    c = "37.8674910"
    d = "-122.2517262"

    print("Calculating Route from Memorial Stadium to the Greek!")

    memorial_lat = "37.869857"
    memorial_lon = "-122.252294"

    soda_lat = "37.873401"
    soda_lon = "-122.254973"

    session.findPath((a, b), (c, d), SUN_WEIGHT)


test()

