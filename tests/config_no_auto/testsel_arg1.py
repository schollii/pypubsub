def test_import():
    from pubsub import setuparg1
    from pubsub import pub       # pubsub3 module
    assert pub.VERSION_API == 3
