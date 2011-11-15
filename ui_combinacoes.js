function UI_combinacoes(id)
{
    var self = this;

    var d2 = document.getElementById(id);
    d2.style.textAlign = "center";
    self.selecao_atual = document.createElement("input");
    self.selecao_atual.style.fontFamily = "monospace";
    self.selecao_atual.style.fontSize   = "11px";
    self.selecao_atual.style.width      = "30px";
    self.selecao_atual.style.height     = "13px";
    self.selecao_atual.value = 0;
    self.selecao_atual.onchange = function () { self.changed(this.value); };
    d2.appendChild(document.createTextNode("Combina\u00e7\u00f5es "));
    var button = document.createElement("span");
    button.style.MozUserSelect = "none";
    button.style.KhtmlUserSelect = "none";
    button.style.border = "1px solid black";
    button.style.backgroundColor = "lightblue";
    button.style.cursor = "pointer";
    button.innerHTML = "<strong>&nbsp;<&nbsp;</strong>";
    button.onselectstart = function () { return false; };
    button.onclick = function () { self.previous(); return false; };
    if (navigator.userAgent.toLowerCase().indexOf("msie") > -1) {
        button.ondblclick = function () { self.previous(); };
    }
    d2.appendChild(button);
    d2.appendChild(document.createTextNode(" "));
    d2.appendChild(self.selecao_atual);
    d2.appendChild(document.createTextNode("/"));
    var numero_selecoes = document.createTextNode("0");
    d2.appendChild(numero_selecoes);
    d2.appendChild(document.createTextNode(" "));
    var button = document.createElement("span");
    button.style.MozUserSelect = "none";
    button.style.KhtmlUserSelect = "none";
    button.style.border = "1px solid black";
    button.style.backgroundColor = "lightblue";
    button.style.cursor = "pointer";
    button.innerHTML = "<strong>&nbsp;>&nbsp;</strong>";
    button.onselectstart = function () { return false; };
    button.onclick = function () { self.next(); return false; };
    if (navigator.userAgent.toLowerCase().indexOf("msie") > -1) {
        button.ondblclick = function () { self.next(); };
    }
    d2.appendChild(button);

    /* procedures */
    self.set_current = function(n) { self.selecao_atual.value = n; };
    self.set_total = function(n) { numero_selecoes.nodeValue = n; };
    /* callbacks */
    self.previous = null;
    self.next     = null;
    self.changed  = null;
}