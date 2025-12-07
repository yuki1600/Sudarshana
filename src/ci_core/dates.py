# src/ci_core/dates.py
from datetime import datetime, timedelta, date, timezone
from timezonefinder import TimezoneFinder
from dateutil import tz
import swisseph as swe
from .constants import PRESSURE_MBAR, TEMP_C

# ---------------------------------
# HistoricalDate Class
# ---------------------------------
class HistoricalDate:
    """
    Represents a date that might be outside Python's datetime range (1-9999).
    Mimics datetime interface for basic attributes and isoformat.
    
    Stores year, month, day, hour, minute, second, microsecond, tzinfo.
    """
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.tzinfo = tzinfo
        
    def isoformat(self):
        # Handle BCE years: -YYYY is represented as negative
        # 0 is 1 BCE, -1 is 2 BCE, etc.
        # ISO 8601 extended format for years outside 0000-9999 requires sign
        sign = "+"
        y_abs = self.year
        if self.year < 0:
            sign = "-"
            y_abs = abs(self.year)
        elif self.year <= 9999: 
            # Normal 4 digit years usually don't need sign in isoformat but 
            # standard datetime.isoformat() uses YYYY-MM-DD
            return f"{self.year:04d}-{self.month:02d}-{self.day:02d}T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
            
        return f"{sign}{y_abs:04d}-{self.month:02d}-{self.day:02d}T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    def strftime(self, fmt):
        """
        Basic strftime implementation for HistoricalDate.
        Only supports common format codes. For full formatting, use isoformat().
        """
        # Replace mostly used codes manually
        s = fmt.replace("%Y", str(self.year))
        s = s.replace("%m", f"{self.month:02d}")
        s = s.replace("%d", f"{self.day:02d}")
        s = s.replace("%H", f"{self.hour:02d}")
        s = s.replace("%M", f"{self.minute:02d}")
        s = s.replace("%S", f"{self.second:02d}")
        if self.tzinfo:
            s = s.replace("%Z", str(self.tzinfo))
        return s

    def __str__(self):
        return self.isoformat()
        
    def utcoffset(self):
        if self.tzinfo:
            # We can't easily rely on standard datetime.utcoffset() if year is out of range
            # because timezone objects often use datetime internally directly.
            # Best effort: return offset for current year or assume fixed offset if possible
            # Or construct a dummy datetime for offset lookup if tz supports it
            try:
                # Create a dummy datetime in 2000 with same month/day/time
                dummy = datetime(2000, self.month, self.day, self.hour, self.minute, self.second, tzinfo=self.tzinfo)
                return dummy.utcoffset()
            except:
                return None
        return None
        
    def date(self):
        """Return a date-like object (self) for compatibility"""
        return self

    def weekday(self):
        """
        Calculate day of week (0=Monday, 6=Sunday) using Zeller's congruence
        """
        Y = self.year
        m = self.month
        q = self.day
        
        if m < 3:
            m += 12
            Y -= 1
            
        # Zeller's congruence
        # h = (q + 13(m+1)/5 + K + K/4 + J/4 + 5J) mod 7
        # where K = year of century (Y % 100), J = zero-based century (Y / 100)
        
        # For Python's weekday(): 0=Mon, ... 6=Sun.
        # Zeller's h: 0=Sat, 1=Sun, 2=Mon...
        
        K = Y % 100
        J = Y // 100
        
        h = (q + int(13*(m+1)/5) + K + int(K/4) + int(J/4) + 5*J) % 7
        
        # Convert Zeller h to Python weekday
        # Zeller: Sat(0), Sun(1), Mon(2) ... Fri(6)
        # Python: Mon(0) ... Sat(5), Sun(6)
        # Map: 2->0, 3->1, ..., 0->5, 1->6
        
        calc_map = {0: 5, 1: 6, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4}
        return calc_map[h]

    def __sub__(self, other):
        """Subtract timedelta from HistoricalDate or calculate difference between dates"""
        if isinstance(other, timedelta):
            # approximate implementation
            # Convert to JD, subtract days, convert back?
            # Or just handle simple cases
            new_second = self.second - other.seconds
            new_minute = self.minute
            new_hour = self.hour
            new_day = self.day
            # This is complex to implement fully without full calendar logic.
            # Use swisseph for JD conversion if possible or simple math
            # Fallback: Ignore for now or implementing minimal logic
            # Just return self (bad) or raise error?
            # Let's try simple JD conversion using swisseph
            jd = swe.julday(self.year, self.month, self.day, self.hour + self.minute/60.0 + self.second/3600.0)
            new_jd = jd - (other.days + other.seconds/86400.0)
            y, m, d, h_dec = swe.revjul(new_jd)
            h = int(h_dec)
            mn = int((h_dec - h) * 60)
            sc = int(((h_dec - h) * 60 - mn) * 60)
            return HistoricalDate(y, m, d, h, mn, sc, self.tzinfo)
            
        elif isinstance(other, (HistoricalDate, datetime, date)):
             # Return timedelta
             jd1 = swe.julday(self.year, self.month, self.day, self.hour + self.minute/60.0 + self.second/3600.0)
             y2 = getattr(other, 'year', 1)
             m2 = getattr(other, 'month', 1)
             d2 = getattr(other, 'day', 1)
             h2 = getattr(other, 'hour', 0)
             mn2 = getattr(other, 'minute', 0)
             s2 = getattr(other, 'second', 0)
             jd2 = swe.julday(y2, m2, d2, h2 + mn2/60.0 + s2/3600.0)
             return timedelta(days=jd1 - jd2)
        else:
            return NotImplemented

    def __add__(self, other):
        """Add timedelta to HistoricalDate"""
        if isinstance(other, timedelta):
            jd = swe.julday(self.year, self.month, self.day, self.hour + self.minute/60.0 + self.second/3600.0)
            new_jd = jd + (other.days + other.seconds/86400.0)
            y, m, d, h_dec = swe.revjul(new_jd)
            h = int(h_dec)
            mn = int((h_dec - h) * 60)
            sc = int(((h_dec - h) * 60 - mn) * 60)
            return HistoricalDate(y, m, d, h, mn, sc, self.tzinfo)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'HistoricalDate' and '{type(other).__name__}'")
    
    def __lt__(self, other):
        """Less than comparison"""
        if isinstance(other, (HistoricalDate, datetime, date)):
            return (self.year, self.month, self.day, self.hour, self.minute, self.second) < \
                   (other.year, other.month, other.day, getattr(other, 'hour', 0), getattr(other, 'minute', 0), getattr(other, 'second', 0))
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal comparison"""
        return self < other or self == other
    
    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, (HistoricalDate, datetime, date)):
            return (self.year, self.month, self.day, self.hour, self.minute, self.second) == \
                   (other.year, other.month, other.day, getattr(other, 'hour', 0), getattr(other, 'minute', 0), getattr(other, 'second', 0))
        return False

# ---------------------------------
# Tiny helpers / Timezone
# ---------------------------------
_tf = TimezoneFinder()

def fmt_dt(dt): return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

def tz_from_latlon(lat: float, lon: float) -> str:
    name = _tf.timezone_at(lat=lat, lng=lon) or _tf.certain_timezone_at(lat=lat, lng=lon)
    if not name:
        raise ValueError("Could not determine timezone for the given coordinates.")
    return name

def local_and_utc(y, m, d, hh, mm, ss, lat, lon, tzname_override: str | None = None):
    """
    Build timezone-aware local and UTC datetimes.
    If tzname_override is provided, use that tz (e.g., 'Asia/Kolkata') instead of inferring from lat/lon.
    """
    if tzname_override:
        tzname = tzname_override
    else:
        tzname = tz_from_latlon(lat, lon)

    local_zone = tz.gettz(tzname)
    if local_zone is None:
        raise ValueError(f"Could not resolve timezone '{tzname}'")

    try:
        dt_local = datetime(y, m, d, hh, mm, ss, tzinfo=local_zone)
        dt_utc   = dt_local.astimezone(timezone.utc)
        tz_offset_hours = dt_local.utcoffset().total_seconds() / 3600.0
    except (ValueError, OverflowError):
        # Fallback for historical dates
        # Estimate offset using current standard offset for the zone
        offset_td = local_zone.utcoffset(datetime.now(timezone.utc)) or timedelta(0)
        tz_offset_hours = offset_td.total_seconds() / 3600.0
        dt_local = HistoricalDate(y, m, d, hh, mm, ss, tzinfo=local_zone)
        dt_utc = HistoricalDate(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
        
    return dt_local, dt_utc, tz_offset_hours, tzname, local_zone

def datetime_to_jd(dt_obj):
    """Convert datetime (or HistoricalDate) to Julian Day (UT)"""
    if hasattr(dt_obj, 'tzinfo') and dt_obj.tzinfo is not None:
        # Convert to UTC first if possible
        if hasattr(dt_obj, 'astimezone'):
            dt_utc = dt_obj.astimezone(timezone.utc)
        else:
            # HistoricalDate custom handling usually doesn't do astimezone easily without pytz/zoneinfo logic
            # Assume naive if it fails or rely on manual offset
             dt_utc = dt_obj # Placeholder: logic for HistoricalDate TZ conversion is limited
    else:
        # Assume naive is UTC or use system? Better to assume UTC for calculations
        dt_utc = dt_obj
        
    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day
    h = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    return swe.julday(y, m, d, h)

def jd_to_datetime(jd, tzname="UTC"):
    """Convert Julian Day (UT) to timezone-aware datetime (or HistoricalDate)"""
    y, m, d, h_dec = swe.revjul(jd)
    h = int(h_dec)
    rem = (h_dec - h)*60
    mn = int(rem)
    sc = int((rem - mn)*60)
    
    # Try creating standard datetime
    target_zone = tz.gettz(tzname) or timezone.utc
    try:
        # First create UTC
        dt_utc = datetime(y, m, d, h, mn, sc, tzinfo=timezone.utc)
        return dt_utc.astimezone(target_zone)
    except (ValueError, OverflowError):
        # Fallback to HistoricalDate
        # Note: HistoricalDate doesn't do complex TZ conversions.
        # We'll just tag it with the target zone but the time/date will be in UT roughly unless we manually offset
        # For simplicity in extreme dates, return UT marked as target or simple UT.
        return HistoricalDate(y, m, d, h, mn, sc, tzinfo=timezone.utc) # Returning UTC for safety in historical
