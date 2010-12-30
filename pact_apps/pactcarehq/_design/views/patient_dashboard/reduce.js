function (keys, values, rereduce) {
//    ret_dict['count'] = 1;
 //       ret_dict['encounter_date'] = get_encounter_date(doc.form);
  //      ret_dict['doc_id'] = doc._id;
   //     ret_dict['chw_id'] = get_user_id(doc.form);
    //    ret_dict['last_xmlns'] = doc.xmlns;
     //   ret_dict['last_received'] = doc.received_on;
    var ret = {};
    ret['count'] = 0;
    ret['encounter_date'] = undefined;
    for (var i = 0; i < values.length; i += 1) {
        ret['count'] += values[i]['count'];
        if (ret['encounter_date'] == undefined || ret['encounter_date'] < values[i]['encounter_date']) {
            ret['encounter_date'] = values[i]['encounter_date'];
            ret['doc_id'] = values[i]['doc_id'];
            ret['chw_id'] = values[i]['chw_id'];
            ret['last_xmlns'] = values[i]['last_xmlns'];
            ret['last_received'] = values[i]['last_received'];
        }
        if(ret['last_bloodwork'] == undefined || ret['last_bloodwork'] < values[i]['last_bloodwork']) {
            ret['last_bloodwork'] = values[i]['last_bloodwork'];
        }
    }
    return ret;
}