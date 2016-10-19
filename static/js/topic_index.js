var app = function() {

    self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Sortable fields in table.
    var sortable = ['title', 'score', 'num_reviews'];

    function reset_sort() {
        for (var i = 0; i < sortable.length; i++) {
            self.vue.is_sort_up[sortable[i]] = false;
            self.vue.is_sort_down[sortable[i]] = false;
        }
    }

    self.toggle_sort = function (col) {
        // Toggle the sort for a given column.
        // The default is to sort down (from largest to smallest).
        var is_down = self.vue.is_sort_down[col];
        reset_sort();
        if (is_down) {
            self.vue.is_sort_up[col] = true;
        } else {
            self.vue.is_sort_down[col] = true;
        }
        self.get_papers();
    };

    function get_url(start_idx, end_idx) {
        var pp = {
            start_idx: start_idx,
            end_idx: end_idx,
            primary_papers: self.vue.primary_papers
        };
        for (var i = 0; i < sortable.length; i++) {
            var k = sortable[i];
            if (self.vue.is_sort_up[k]) {
                pp['sort_' + k] = 'up';
            } else if (self.vue.is_sort_down[k]) {
                pp['sort_' + k] = 'down';
            }
        }
        return "/api/topic_papers/" + topic_id + "?" + $.param(pp);
    }

    // Function to get the data.
    self.get_papers = function () {
        $.getJSON(get_url(0, 20), function (data) {
            self.vue.has_more = data.has_more;
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
        self.get_papers();
    };

    self.get_more_papers = function () {
        var num_papers = self.vue.papers.length;
        $.getJSON(get_url(num_papers, num_papers + 50), function (data) {
            self.vue.has_more = data.has_more;
            self.extend(self.vue.papers, data.papers);
        });
    };

    self.vue = new Vue({
        el: "#topics-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            papers: [],
            primary_papers: true,
            show_paper_scores: false,
            can_review: false,
            can_add_paper: false,
            has_more: false,
            is_sort_up: {'title': false, 'score': false, 'num_reviews': false},
            is_sort_down: {'title': false, 'score': true, 'num_reviews': false}
        },
        methods: {
            set_scores: self.set_scores,
            set_primary: self.set_primary,
            toggle_sort: self.toggle_sort,
            get_more_papers: self.get_more_papers
        }
    });

    self.get_papers();
    $("#topics-div").show();

    return self;
};

var APP = null;
jQuery(function(){APP = app();});
