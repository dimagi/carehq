//basic enhancements for really basic image manipulations
function reset_all(div_id) {
    Pixastic.revert(document.getElementById(div_id));
}

function histogram(div_id) {
    Pixastic.process(document.getElementById(div_id), "histogram", {
        average : false, paint:true,color:"rgba(255,255,255,0.5)",
    });
}

function remove_noise(div_id) {
    Pixastic.process(document.getElementById(div_id), "removenoise");
}

function usm(div_id) {
    Pixastic.process(document.getElementById(div_id), "unsharpmask", {
        amount : 150,
        radius : 1.25,
        threshold : 12,
    });

}


function color_histogram(div_id) {
    Pixastic.process(document.getElementById(div_id), "colorhistogram", {
        paint:true,
    });
}

function laplace(div_id) {
    Pixastic.process(document.getElementById(div_id), "laplace", {
        edgeStrength : 0.9,
        greyLevel : 4,
        invert : false,
    })

}

function edge_detection(div_id) {
    Pixastic.process(document.getElementById(div_id), "edges", {
        mono : false,
        invert : false
    });
}

function edge_detection2(div_id) {
    Pixastic.process(document.getElementById(div_id), "edges2");
}

function emboss(div_id) {
    Pixastic.process(document.getElementById(div_id), "emboss", {
        strength : 2.5,
        greyLevel : 166,
        direction : 'topleft',
        blend : false
    });
}