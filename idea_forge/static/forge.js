/* Custom listboxes over the native selects. The select stays in the form. */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  function enhanceSelect(select) {
    if (select.getAttribute("data-enhanced") === "1") {
      return;
    }
    select.setAttribute("data-enhanced", "1");

    var shell = select.parentNode;
    var host = shell && shell.classList && shell.classList.contains("select-shell") ? shell : select;
    var picker = document.createElement("div");
    picker.className = "picker";
    host.parentNode.insertBefore(picker, host);
    picker.appendChild(host);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "picker__button";
    button.setAttribute("aria-haspopup", "listbox");
    button.setAttribute("aria-expanded", "false");

    var valueEl = document.createElement("span");
    valueEl.className = "picker__value";
    var mark = document.createElement("span");
    mark.className = "picker__mark";
    mark.setAttribute("aria-hidden", "true");
    button.appendChild(valueEl);
    button.appendChild(mark);

    var list = document.createElement("ul");
    list.className = "picker__list";
    list.setAttribute("role", "listbox");
    list.hidden = true;

    if (select.id) {
      button.id = select.id + "-button";
      valueEl.id = select.id + "-value";
      list.id = select.id + "-list";
      button.setAttribute("aria-controls", list.id);
    }

    var options = [];
    var active = select.selectedIndex >= 0 ? select.selectedIndex : 0;
    var buffer = "";
    var bufferTimer = 0;

    function paint() {
      if (!select.options.length) {
        valueEl.textContent = "";
        return;
      }
      var selected = select.selectedIndex;
      if (selected < 0) {
        selected = 0;
      }
      valueEl.textContent = select.options[selected].text;
      for (var n = 0; n < options.length; n++) {
        var on = n === selected;
        options[n].setAttribute("aria-selected", on ? "true" : "false");
        if (n === active) {
          options[n].classList.add("is-active");
        } else {
          options[n].classList.remove("is-active");
        }
      }
      if (!list.hidden && options[active]) {
        button.setAttribute("aria-activedescendant", options[active].id);
        reveal(options[active]);
      } else {
        button.removeAttribute("aria-activedescendant");
      }
    }

    function reveal(item) {
      var listRect = list.getBoundingClientRect();
      var itemRect = item.getBoundingClientRect();
      if (itemRect.bottom > listRect.bottom) {
        list.scrollTop += itemRect.bottom - listRect.bottom;
      } else if (itemRect.top < listRect.top) {
        list.scrollTop -= listRect.top - itemRect.top;
      }
    }

    function closeOthers() {
      var lists = document.querySelectorAll(".picker__list");
      for (var n = 0; n < lists.length; n++) {
        if (lists[n] === list || lists[n].hidden) {
          continue;
        }
        lists[n].hidden = true;
        var other = lists[n].parentNode && lists[n].parentNode.querySelector(".picker__button");
        if (other) {
          other.setAttribute("aria-expanded", "false");
          other.removeAttribute("aria-activedescendant");
        }
      }
    }

    function openList() {
      closeOthers();
      list.hidden = false;
      button.setAttribute("aria-expanded", "true");
      active = select.selectedIndex >= 0 ? select.selectedIndex : 0;
      paint();
    }

    function closeList() {
      if (list.hidden) {
        return;
      }
      list.hidden = true;
      button.setAttribute("aria-expanded", "false");
      button.removeAttribute("aria-activedescendant");
    }

    function choose(index, closeAfter) {
      if (!options.length) {
        return;
      }
      if (index < 0) {
        index = 0;
      }
      if (index >= options.length) {
        index = options.length - 1;
      }
      active = index;
      var changed = select.selectedIndex !== index;
      select.selectedIndex = index;
      paint();
      if (changed) {
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      if (closeAfter) {
        closeList();
      }
    }

    function move(delta) {
      var wasClosed = list.hidden;
      if (wasClosed) {
        openList();
      }
      var start = wasClosed ? select.selectedIndex : active;
      if (start < 0) {
        start = 0;
      }
      choose(start + delta, false);
    }

    function jump(index) {
      if (list.hidden) {
        openList();
      }
      choose(index, false);
    }

    function typeahead(ch) {
      buffer += ch.toLowerCase();
      window.clearTimeout(bufferTimer);
      bufferTimer = window.setTimeout(function () {
        buffer = "";
      }, 700);
      if (!options.length) {
        return;
      }
      var start = active + 1;
      for (var n = 0; n < options.length; n++) {
        var index = (start + n) % options.length;
        if (options[index].textContent.toLowerCase().indexOf(buffer) === 0) {
          if (list.hidden) {
            openList();
          }
          choose(index, false);
          return;
        }
      }
    }

    for (var i = 0; i < select.options.length; i++) {
      (function (index) {
        var source = select.options[index];
        var item = document.createElement("li");
        item.className = "picker__option";
        item.setAttribute("role", "option");
        item.id = (select.id || "picker") + "-opt-" + index;
        item.textContent = source.text;
        item.setAttribute("aria-selected", source.selected ? "true" : "false");
        item.addEventListener("pointerdown", function (event) {
          event.preventDefault();
          choose(index, true);
          button.focus();
        });
        list.appendChild(item);
        options.push(item);
      })(i);
    }

    picker.appendChild(button);
    picker.appendChild(list);

    var field = picker.parentNode;
    if (field && select.id) {
      var labels = field.getElementsByTagName("label");
      for (var n = 0; n < labels.length; n++) {
        if (labels[n].htmlFor === select.id) {
          if (!labels[n].id) {
            labels[n].id = select.id + "-label";
          }
          button.setAttribute("aria-labelledby", labels[n].id + " " + valueEl.id);
          list.setAttribute("aria-labelledby", labels[n].id);
          labels[n].htmlFor = button.id;
          break;
        }
      }
    }

    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");
    paint();
    picker.classList.add("is-ready");

    button.addEventListener("click", function () {
      if (list.hidden) {
        openList();
      } else {
        closeList();
      }
    });

    button.addEventListener("keydown", function (event) {
      var key = event.key;
      if (key === "ArrowDown") {
        event.preventDefault();
        move(1);
      } else if (key === "ArrowUp") {
        event.preventDefault();
        move(-1);
      } else if (key === "Home") {
        event.preventDefault();
        jump(0);
      } else if (key === "End") {
        event.preventDefault();
        jump(options.length - 1);
      } else if (key === "Escape") {
        if (!list.hidden) {
          event.preventDefault();
          closeList();
        }
      } else if (key === "Enter") {
        if (!list.hidden) {
          event.preventDefault();
          closeList();
        }
      } else if (key === " ") {
        event.preventDefault();
        if (list.hidden) {
          openList();
        } else {
          closeList();
        }
      } else if (key === "Tab") {
        closeList();
      } else if (key && key.length === 1 && !event.altKey && !event.ctrlKey && !event.metaKey) {
        event.preventDefault();
        typeahead(key);
      }
    });

    document.addEventListener("pointerdown", function (event) {
      if (!picker.contains(event.target)) {
        closeList();
      }
    });
  }

  var selects = document.querySelectorAll("select");
  for (var s = 0; s < selects.length; s++) {
    enhanceSelect(selects[s]);
  }
}());
