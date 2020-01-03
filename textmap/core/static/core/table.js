"use strict";
console.debug('table.js loaded');


const columnCount = 6;
const textColumn = 3;
const cellConstructors = {
    1: function(_) {
        let td = document.createElement('td');
        td.className = 'paragraph-table-left table-minimal';
        let div = document.createElement('div');
        let label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        label.append(input);
        div.append(label);
        td.append(div);
        return td;
    },
    2: function(_) {
        let td = document.createElement('td');
        td.classList.add('paragraph-table-left', 'table-minimal');
        td.innerHTML = '&rangle;';
        return td;
    },
    3: function(rowData) {
        let td = document.createElement('td');
        td.className = 'paragraph-table-main';
        const last = rowData.sentences.pop();
        for (const s of rowData.sentences) {
            const text = document.createTextNode(s.raw);
            let a = document.createElement('a');
            a.className = 'mark-paragraph-split';
            a.addEventListener('click',
                () => handlerParagraphSplit(s.id)
            );
            td.append(text, a);
        }
        rowData.sentences.push(last);
        const lastText = document.createTextNode(last.raw);
        td.append(lastText);
        return td;
    },
    4: function(rowData) {
        let td = document.createElement('td');
        td.classList.add('paragraph-table-right', 'table-minimal');
        let div = document.createElement('div');
        let a1 = document.createElement('a');
        a1.className = 'button';
        a1.addEventListener('click',
            () => handlerParagraphConcat(rowData.uid, 'prev')
        );
        a1.innerText = '^';
        let a2 = document.createElement('a');
        a2.className = 'button';
        a2.addEventListener('click',
            () => handlerParagraphConcat(rowData.uid, 'next')
        );
        a2.innerText = 'v';
        div.prepend(a1, ' ', a2);
        td.prepend(div);
        return td;
    }
};

function tableInsertLine(afterUid, insertUid, sentences) {
    const afterLine = document.getElementById(afterUid);

    let newLine = document.createElement('tr');
    newLine.id = insertUid;
    const rowData = {
        uid: insertUid,
        sentences: sentences
    };
    const cells = [...Array(columnCount).keys()].map(i => tableInitCell(rowData, i));

    newLine.prepend(...cells);
    afterLine.after(newLine);
    return 0;
}

function tableInitCell(rowData, nCol) {
    // Table Cell general constructor
    const defaultConstructor = (_) => document.createElement('td');

    return (cellConstructors.hasOwnProperty(nCol)
        ? cellConstructors[nCol](rowData)
        : defaultConstructor(rowData)
    );
}

function tableRemoveLine(uid) {
    document.getElementById(uid).remove();
    return 0;
}

function tableAlterLine(uid, sentences) {
    let td = cellConstructors[textColumn]({uid: uid, sentences: sentences});
    const tr = document.getElementById(uid);
    tr.children[textColumn].replaceWith(td);
    return 0;
}
