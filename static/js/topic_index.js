var app = function() {

    self = {};

    Vue.config.silent = false; // show all warnings

    // The list of papers.
    self.papers = [];

    self.vue = new Vue({
        el: "#topics-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        mounted: get_data,
        data: {
            papers: self.papers,
            show_paper_scores: false
        }
    });

    function get_data() {
        var url = "/api/topic_papers/" + topic_id;
        $.getJSON(url, function (data) {
            self.papers = data.papers;
            self.vue.papers = data.papers;
        })
    }

    get_data();
    $("#topics-div").show();
    return self;
};

var APP = null;
jQuery(function(){APP = app();});
