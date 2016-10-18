var app = function() {

    self = {};

    Vue.config.delimiters = ['({', '})'];
    Vue.config.unsafeDelimiters = ['!{', '}'];
    Vue.config.silent = false; // show all warnings
    Vue.config.async = true; // for debugging only

    // The list of papers.
    self.papers = [];

    self.vue = new Vue({
        el: "#topics-div",
        mounted: get_data,
        data: {
            papers: self.papers,
            show_paper_scores: false
        }
    });

    function get_data() {
        var url = "/api/topic_papers/" + topic_id;
        $.getJSON(url, function (data) {
            self.vue.papers = data.papers;
        })
    }

    return self;
};

var APP = null;
jQuery(function(){APP = app();});
