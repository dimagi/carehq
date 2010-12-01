function (keys, values, rereduce) {
    //keys = ['chw_username', <day_of_week_integer>']
    //values = CDotWeeklySchedule single day, eg {pact_id, active_date, schedule_index, ended_date}
    //return sum(values);
    if (rereduce == true) {
        
    } else {
        for (var i = 0; i < values.length; i++) {
            var ret = {};
            if (values[i]['day_of_week'] in ret == false) {
                ret[values[i]['day_of_week']] = []    
            }
            ret[values[i]['day_of_week']].push(values);        
        }
        return ret;
    }


}