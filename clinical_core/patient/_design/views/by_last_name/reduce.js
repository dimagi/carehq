function (keys, values, rereduce) {
    if (!rereduce) {
        return values.length;
    }
    else {
        return sum(values);
    }
}