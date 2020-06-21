
let tag_combos = null;
let tag_meta = null;
let tag_selected = null;


$(document).ready(async function () {
    
    const resp_tag_meta = fetch("/get_tagmeta");
    const resp_tag_selection = fetch("/get_selection");
    const resp_tag_combos = fetch("/get_tagcombinations");
    const result = await Promise.all([
        resp_tag_combos,
        resp_tag_meta,
        resp_tag_selection
    ]);
    const content = await Promise.all(result.map(i => i.json()));

    tag_combos = content[0];
    tag_meta = content[1];
    tag_selected = content[2];

    Object.getOwnPropertyNames(tag_meta).forEach(i => {
        $("#tag-selected-" + i).click(function () {
            tag_selected = jQuery.grep(tag_selected, function(value) {
                return value != i;
            });
            update_visible_tags();
        });
        
        $("#tag-available-" + i).click(function () {
            tag_selected.push(i)
            update_visible_tags();
        });
    });
    
    $("#button-submit").click(async () => {
        let resp = await fetch("/set_selection", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "selection": tag_selected })
        });
        window.location.replace("/");
    })
    
    
    update_visible_tags();
    $("#page-content").show();
});



function get_additional_tags(doc_items){
    let extras = []
    const has_all_tags = tag_selected.every(x => doc_items.includes(x));
    if (has_all_tags) {
        doc_items.forEach(i => {
            if (!tag_selected.includes(i)) {
                extras.push(i)
            }
        })
    }
    return extras
}



function update_visible_tags() {
    let possible_values = Object.values(tag_combos).flatMap(i => get_additional_tags(i))
    let unique_possible_values = [...new Set(possible_values)];
    
    Object.keys(tag_meta).forEach(tag => {
        
        if (tag_selected.length === 0) {
            $("#tag-available-" + tag).show();
            $("#tag-selected-" + tag).hide();
        } else {
            if (!unique_possible_values.includes(tag)) {
                $("#tag-available-" + tag).hide()
            } else {
                $("#tag-available-" + tag).show()
            }
            
            if (tag_selected.includes(tag)) {
                $("#tag-selected-" + tag).show()
            } else {
                $("#tag-selected-" + tag).hide()
            }
        }
    });
}

// tag_meta
//
// COMPUTING:
//     RANK: 1
//     NAME: "Computing"
// NETWORK:
//     RANK: 2
//     NAME: "Networking"

// tag_selection
// [ A, B, C]

// KA_INTRO_BIO_01:
//     0: "BIOLOGY"
//     1: "COURSE"
//     2: "CHEMISTRY"
// KA_INTRO_BIO_02: 
//     0: "BIOLOGY"
//     1: "COURSE"
//     2: "CHEMISTRY"





