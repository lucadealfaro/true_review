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
            primary_papers: true,
            show_paper_scores: false,
            show_all_papers: true,
            can_review: false,
            can_add_paper: false
        }
    });

    function get_data() {
        var url = "/api/topic_papers/" + topic_id;
        $.getJSON(url, function (data) {
            self.papers = data.papers;
            self.vue.papers = data.papers;
            self.vue.can_review = data.can_review;
            selv.vue.can_add_paper = data.can_add_paper;
        })
    }

    get_data();
    $("#topics-div").show();
    return self;
};

var APP = null;
jQuery(function(){APP = app();});
