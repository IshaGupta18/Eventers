// console.log("yayy");
// var x='{{ main_event_list[0][0] }}'
// console.log(x);
// var t=document.getElementById(x);
// console.log(t)
function createDropDown(itemList,id_index,value_index,prefix,prefix_id_select){
    let component="<select id="+prefix_id_select+">";
    let n=length(itemList);
    for (let i=0;i<n;i++){
        let temp="<option id="+prefix+"_"+itemList[i][id_index]+">"+itemList[i][value_index]+"</option>";
        component+=temp;
    }
    component+="</select>";
    return component;
}
function getSelectedOption(selectID){
    let selectMenu = document.getElementById(selectID);
    return selectMenu.options[selectMenu.selectedIndex].id;
}