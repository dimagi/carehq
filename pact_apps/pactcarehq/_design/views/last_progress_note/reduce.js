function (keys, values, rereduce) {
    function sort_arr(a,b) {
        if (a[1] > b[1]) {
            return -1;
        }
        if (a[1] == b[1]) {
            return 0;
        }
        if (a[1] < b[1]) {
            return 1;
        }
    }
    if (rereduce) {
        //receiving arrays:
        //[ [doc_id, encounter_date], ...]
        var combined = [];
        for (var i = 0; i < values.length; i+=1) {
            for(var j = 0; j < values[i].length; j+=1)  {
                combined.push(values[i][j]);
            }
        }
        combined.sort(sort_arr);
        if (combined.length >= 3) {
            return combined.slice(0,3);
        } else {
            return combined;
        }

        return ret;
    } else {
        values.sort(sort_arr);
        //returns an array:
        //[ [doc_id, encounter_date], ...]
        if (values.length >= 3) {
            return values.slice(0,3);
        } else {
            return values;
        }
    }
}
