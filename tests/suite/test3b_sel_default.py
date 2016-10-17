def test_import():
    from pubsub import pub
    assert pub.VERSION_API == 4
