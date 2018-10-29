var columns = [
    ['followers', 'tweets', 'friends', 'favorites'], // Stats
    ['favorites', 'retweets', 'updated', 'tweetExists'], // Tweets
    ['a', 'b', 'c'], // Posts
    ['a', 'b', 'c'] // Follows
]

window.onload = init;

function init(){
    var selectTable = document.getElementById("select-table").onchange = selectTableOnClick;
    selectTableOnClick();
}

function selectTableOnClick(){
    let selectTable = document.getElementById("select-table");
    let selectColumn = document.getElementById("select-column");
    selectColumn.innerHTML = "";
    for(var i = 0; i < columns[selectTable.selectedIndex].length; i++){
        selectColumn.append(createOptionElement(columns[selectTable.selectedIndex][i]));
    }
}

function createOptionElement(val){
    var option = document.createElement("option")
    option.value = val;
    option.innerHTML = val.charAt(0).toUpperCase() + val.slice(1);
    return option;
}