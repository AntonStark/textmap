"use strict";
console.debug('interactive.js loaded');


function handlerParagraphConcat(uuid, mode) {
    console.debug('handlerParagraphConcat', uuid, mode);
    let req = new XMLHttpRequest();
    req.open('GET', `/textmap/paragraph_concat/${uuid}?mode=${mode}`);
    req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    req.setRequestHeader('X-CSRFToken', csrftoken);
    req.onreadystatechange = function () {
        if (this.readyState === 4) {
            const res = JSON.parse(this.responseText);
            console.log(this.status, res);
            tableAlterLine(res['paragraph_changed']['uid'],
                res['paragraph_changed']['sentences']);
            tableRemoveLine(res['paragraph_removed']['uid']);
        }
        else {
            console.log(this.readyState);
        }
    };

    req.send();
    console.log('handlerParagraphConcat', 'done');
}

function handlerParagraphSplit(sentence_id) {
    console.debug('handlerParagraphSplit', sentence_id);
    let req = new XMLHttpRequest();
    req.open('GET', `/textmap/paragraph_split/${sentence_id}`);
    req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    req.setRequestHeader('X-CSRFToken', csrftoken);
    req.onreadystatechange = function () {
        if (this.readyState === 4) {
            const res = JSON.parse(this.responseText);
            console.debug(this.status, res);
            let s = tableInsertLine(res['target_paragraph']['uid'],
                res['created_paragraph']['uid'],
                res['created_paragraph']['sentences']);
            if (s !== 0)
                console.error('handlerParagraphSplit', 'tableInsertLine -> ', s);

            s = tableAlterLine(res['target_paragraph']['uid'],
                res['target_paragraph']['sentences']);
            if (s !== 0)
                console.error('handlerParagraphSplit', 'tableInsertLine -> ', s);
        }
        else {
            console.debug(this.readyState);
        }
    };

    req.send();
    console.log('handlerParagraphSplit', 'done');
}
