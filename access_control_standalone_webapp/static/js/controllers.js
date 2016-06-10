heliosApp = angular.module('heliosApp', []).config(function($interpolateProvider){
    $interpolateProvider.startSymbol('{[{').endSymbol('}]}'); //because Flask's Jinga2 templating engine already uses curly braces (just like as AngularJS ) for templating, we'll make Angular use something else
});


heliosApp.controller('homeController', function($scope) {
        
        $scope.message = 'Everyone come and see how good I look!';
    });

heliosApp.controller('userManagementController', function($scope) {
        $scope.message = 'Look! I am an about page.';
    });

   