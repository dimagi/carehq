
jQuery.fn.dataTableExt.oSort['pretty_time-desc'] = function(a, b) {
	if (a.indexOf("ago") >= 0) {
		a = a.replace("ago", "");
		if (b.indexOf("ago") >= 0) {
			b = b.replace("ago", "");
			return compare_times(a, b);
		} 
		else {
			return 1;
		}
	} else if (a.indexOf("from") >= 0) {
		a = a.replace("from now", "");
		if (b.indexOf("from") >= 0) {
			b = b.replace("from now", "");
			return (-1 * compare_times(a, b));
		}
		else {
			return -1;
		}
	}
}

jQuery.fn.dataTableExt.oSort['pretty_time-asc'] = function(a, b) {
	if (a.indexOf("ago") >= 0) {
		a = a.replace("ago", "");
		if (b.indexOf("ago") >= 0) {
			b = b.replace("ago", "");
			return (-1 * compare_times(a, b));
		} 
		else {
			return -1;
		}
	} else if (a.indexOf("from") >= 0) {
		a = a.replace("from now", "");
		if (b.indexOf("from") >= 0) {
			b = b.replace("from now", "");
			return (compare_times(a, b));
		}
		else {
			return 1;
		}
	}
}

function compare_times(a, b) {
	return (convert_to_num(a) > convert_to_num(b)) ? 1 : -1;
}

function convert_to_num(a) {
	if (a.indexOf("years") >= 0) {
		a = a.replace("years", "");
		a = a.trim();
		var num = parseInt(a) * 365 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("year") >= 0) {
		a = a.replace("year", "");
		a = a.trim();
		var num = 365 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("months") >= 0) {
		a = a.replace("months", "");
		a = a.trim();
		var num = parseInt(a) * 30 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("month") >= 0) {
		a = a.replace("month", "");
		a = a.trim();
		var num = 30 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("weeks") >= 0) {
		a = a.replace("weeks", "");
		a = a.trim();
		var num = parseInt(a) * 7 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("week") >= 0) {
		a = a.replace("week", "");
		a = a.trim();
		var num = 7 * 24 * 3600;
		return num;
	}
	else if (a.indexOf("days") >= 0) {
		a = a.replace("days", "");
		a = a.trim();
		var num = parseInt(a) * 24 * 3600;
		return num;
	}
	else if (a.indexOf("day") >= 0) {
		a = a.replace("day", "");
		a = a.trim();
		var num = 24 * 3600;
		return num;
	}
	else if (a.indexOf("hours") >= 0) {
		a = a.replace("hours", "");
		a = a.trim();
		var num = parseInt(a) * 3600;
		return num;
	}
	else if (a.indexOf("hour") >= 0) {
		a = a.replace("hour", "");
		a = a.trim();
		var num = 3600;
		return num;
	}
	else if (a.indexOf("minutes") >= 0) {
		a = a.replace("minutes", "");
		a = a.trim();
		var num = parseInt(a) * 60;
		return num;
	}
	else if (a.indexOf("minute") >= 0) {
		a = a.replace("minute", "");
		a = a.trim();
		var num = 60;
		return num;
	}
	else if (a.indexOf("seconds") >= 0) {
		a = a.replace("seconds", "");
		a = a.trim();
		var num = parseInt(a);
		return num;
	}
	else if (a.indexOf("second") >= 0) {
		a = a.replace("second", "");
		a = a.trim();
		var num = 1;
		return num;
	}
}