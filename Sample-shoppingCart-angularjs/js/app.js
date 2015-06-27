$(function() {

  $("#catalog").accordion();

});

var App = angular.module('drag-and-drop', ['ngDragDrop']);


App.controller('oneCtrl', function($scope, $timeout) {

  $scope.list1 = [{'title': 'Apple'},{'title': 'Banana'},{'title': 'Mango'}];

  $scope.list2 = [{'title': 'Chicago'},{'title': 'New York'},{'title': 'Dallas'}];

  $scope.list3 = [{'title': 'iPhone'},{'title': 'iPod'},{'title': 'iPad'}];


  $scope.list4 = [];


  $scope.hideMe = function() {

    return $scope.list4.length > 0;

  }

});
