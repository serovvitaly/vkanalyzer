angular.module('VkAnalyzerApp', ['ngMaterial', 'ngCookies'])
    .controller('VkGroupController', function($scope, $http, $cookies) {
        var self = this;
        self.find = function() {
            $http.post('/group/find/', {
                'group_uid': self.groupUid
            }, {
                'headers': {
                    'X-CSRFToken': $cookies.get('csrftoken')
                }
            }).then(
                function(response){
                    console.log('successCallback', response.data);
                },
                function (response) {
                    //console.log('errorCallback', response);
                }
            );
        };
    });