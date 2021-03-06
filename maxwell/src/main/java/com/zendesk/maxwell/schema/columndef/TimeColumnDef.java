package com.zendesk.maxwell.schema.columndef;

import java.sql.Time;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.TimeZone;

import com.google.code.or.common.util.MySQLConstants;

public class TimeColumnDef extends ColumnDefWithLength {
	public TimeColumnDef(String name, String type, int pos, Long columnLength) {
		super(name, type, pos, columnLength);
	}

	@Override
	public boolean matchesMysqlType(int type) {
		return type == MySQLConstants.TYPE_TIME || type == MySQLConstants.TYPE_TIME2;
	}

	protected String formatValue(Object value) {
		if ( value instanceof Timestamp ) {
			Time time = new Time(((Timestamp) value).getTime());
			String timeAsStr = String.valueOf(time);
			return appendFractionalSeconds(timeAsStr, ((Timestamp) value).getNanos(), this.columnLength);

		} else if ( value instanceof Long ) {
			Calendar cal = Calendar.getInstance();
			long milliDiff = cal.get(Calendar.ZONE_OFFSET);
			Time time = new Time(((Long) value / 1000) - milliDiff);
			String timeAsStr = String.valueOf(time);

			return appendFractionalSeconds(timeAsStr, (int) ((Long) value % 1000000) * 1000, this.columnLength);
		} else {
			return String.valueOf((Time) value);
		}
	}
}
