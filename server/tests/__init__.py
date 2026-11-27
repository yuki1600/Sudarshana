from server import auth, settings

auth.REQUIRED = False   # the calculation tests run without an account; test_auth turns the gate back on

# The tests run on fixed settings, whatever the app's defaults (the user's choices: Pushya Paksha and the rest) are:
# True Lahiri,
TEST_AYANAMSA = "TRUE_LAHIRI"
settings.SettingsIn.model_fields["ayanamsa"].default = TEST_AYANAMSA
settings.SettingsIn.model_rebuild(force=True)
next(o for o in settings.OPTIONS if o["key"] == "ayanamsa")["default"] = TEST_AYANAMSA

# and the fixed-orb combustion, nodal exaltation and narrow Shadbala moolatrikona degrees (the app defaults to the classical,
# BPHS ones), equal bhavas, anti-zodiacal bhavas from the nodes and full aspect of 60 (the app's: Sripati, forward, 100),
# mean nodes (the app's: true) and the first Mrityu Bhaga table (the app's: Phala Deepika's)
for _k, _v in (("combustion_classical", False), ("nodal_parasara", False), ("moolatrikona_bphs", False),
               ("house_type", 1), ("bhava_nodes_reversed", True), ("aspect_full", 60), ("nodes", "mean"), ("mrityu_second_table", False)):
    settings.SettingsIn.model_fields[_k].default = _v
    next(o for o in settings.OPTIONS if o["key"] == _k)["default"] = _v
settings.SettingsIn.model_rebuild(force=True)

# Only after the pins above: importing the app builds its request models, which take SettingsIn's defaults as they are then
from server.app import main  # noqa: E402

main.ALLOWED_HOSTS.append("testserver")   # TestClient's default Host; test_security checks the others
