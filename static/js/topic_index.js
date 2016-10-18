var app = function() {

    self = {};

    Vue.config.silent = false; // show all warnings

    // The list of papers.
    self.papers = [];

    // Function to get the data.
    self.get_data = function () {
        var url = "/api/topic_papers/" + topic_id;
        $.getJSON(url, function (data) {
            self.papers = data.papers;
            self.vue.papers = data.papers;
            self.vue.can_review = data.can_review;
            self.vue.can_add_paper = data.can_add_paper;
        })
    };

    // Functions handling buttons.

    self.set_scores = function (b) {
        self.vue.show_paper_scores = b;
    };
    self.set_primary = function(b) {
        self.vue.primary_papers = b;
        // TODO: Reload data. 
    };

    self.vue = new Vue({
        el: "#topics-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        mounted: function () {
            self.get_data();
            $("#topics-div").show();
        },
        data: {
            papers: self.papers,
            primary_papers: true,
            show_paper_scores: false,
            can_review: false,
            can_add_paper: false
        },
        methods: {
            set_scores: self.set_scores
        }
    });

    return self;
};

var APP = null;
jQuery(function(){APP = app();});
