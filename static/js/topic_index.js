var app = function() {

    self = {};

    Vue.config.silent = false; // show all warnings

    // Function to get the data.
    self.get_data = function () {
        var url = "/api/topic_papers/" + topic_id + "?";
        url += $.param({
            requested_num_papers: self.vue.requested_num_papers,
            primary_papers: self.vue.primary_papers,
            sort_by: self.vue.sort_by,
            sort_descending: self.vue.sort_descending
        });
        $.getJSON(url, function (data) {
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
        data: {
            papers: [],
            requested_num_papers: 20,
            primary_papers: true,
            show_paper_scores: false,
            can_review: false,
            can_add_paper: false,
            sort_by: "score",
            sort_descending: true
        },
        methods: {
            set_scores: self.set_scores
        }
    });

    self.get_data();
    $("#topics-div").show();

    return self;
};

var APP = null;
jQuery(function(){APP = app();});
