"""Swiss Ephemeris initialization — shared by chart pipeline and mundane timing."""

import swisseph as swe


def init_ephe(ephe_path="ephe", use_moseph=False, sidereal_mode=swe.SIDM_LAHIRI):
    if not use_moseph:
        swe.set_ephe_path(ephe_path)
    if sidereal_mode is not None:
        swe.set_sid_mode(sidereal_mode)
    ephflag = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
    flags = ephflag | swe.FLG_SPEED
    if sidereal_mode is not None:
        flags |= swe.FLG_SIDEREAL
    return flags
