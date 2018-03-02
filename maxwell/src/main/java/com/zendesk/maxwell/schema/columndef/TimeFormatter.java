package com.zendesk.maxwell.schema.columndef;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.TimeZone;


public class TimeFormatter {
	private static SimpleDateFormat makeFormatter(String format, boolean utc) {
		SimpleDateFormat dateFormatter = new SimpleDateFormat(format);
		//jepson 设置时区为Asia/Shanghai
//		if ( utc )
//			dateFormatter.setTimeZone(TimeZone.getTimeZone("UTC"));
//		dateFormatter.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"));
		Calendar cal = Calendar.getInstance();
		long milliDiff = cal.get(Calendar.ZONE_OFFSET);
		// Got local offset, now loop through available timezone id(s).
		String [] ids = TimeZone.getAvailableIDs();
		String name = null;
		for (String id : ids) {
			TimeZone tz = TimeZone.getTimeZone(id);
			if (tz.getRawOffset() == milliDiff) {
				// Found a match.
				name = id;
				dateFormatter.setTimeZone(tz);
				break;
			}
		}
		return dateFormatter;
	}

	private static SimpleDateFormat dateFormatter           = makeFormatter("yyyy-MM-dd", false);
	private static SimpleDateFormat dateUTCFormatter        = makeFormatter("yyyy-MM-dd", true);
	private static SimpleDateFormat dateTimeFormatter       = makeFormatter("yyyy-MM-dd HH:mm:ss", false);
	private static SimpleDateFormat dateTimeUTCFormatter    = makeFormatter("yyyy-MM-dd HH:mm:ss", true);
}
