function (keys, values, rereduce) {
    function unique(a)
    //source: http://www.martienus.com/code/javascript-remove-duplicates-from-array.html
    {
       var r = new Array();
       o:for(var i = 0, n = a.length; i < n; i++)
       {
          for(var x = 0, y = r.length; x < y; x++)
          {
             if(r[x]==a[i]) continue o;
          }
          r[r.length] = a[i];
       }
       return r;
    }


    //keys = ['chw_username', <day_of_week_integer>']
    //values = CDotWeeklySchedule single day, eg {pact_id, active_date, schedule_index, ended_date}
    //return sum(values);
    if (rereduce == true) {
        //return unique(values);

    } else {
        return unique(values);
    }

}