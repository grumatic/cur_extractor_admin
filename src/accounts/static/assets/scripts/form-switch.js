function changeCreateElementOn() {
    var viewElementArray;

    viewElementArray = document.getElementsByClassName("view");

    for(var i = 0; i < viewElementArray.length; i++)
    {
        viewElementArray[i].setAttribute("class", "view off");
    }

    var viewElementArray;

    viewElementArray = document.getElementsByClassName("create off");

    for(var i = 0; i < viewElementArray.length; i++)
    {
        viewElementArray[i].setAttribute("class", "create");
    }   
}

function changeCreateElementOff() {
    var viewElementArray;

    viewElementArray = document.getElementsByClassName("view off");

    for(var i = 0; i < viewElementArray.length; i++)
    {
        viewElementArray[i].setAttribute("class", "view");
    }

    var viewElementArray;

    viewElementArray = document.getElementsByClassName("create");

    for(var i = 0; i < viewElementArray.length; i++)
    {
        viewElementArray[i].setAttribute("class", "create off");
    }   
}
