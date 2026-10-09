(function () {
  var ufCache = null;

  function norm(s) {
    return (s || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function getUfs() {
    if (!ufCache) {
      ufCache = fetch('/api/ufs').then(function (r) { return r.json(); });
    }
    return ufCache;
  }

  function getMunicipios(sigla) {
    return fetch('/api/municipios?uf=' + encodeURIComponent(sigla)).then(function (r) { return r.json(); });
  }

  function create(root, opts) {
    var input = root.querySelector('.cb-input');
    var hidden = root.querySelector('.cb-hidden');
    var list = root.querySelector('.cb-list');
    var items = [];
    var shown = [];
    var active = -1;

    function fechar() { list.style.display = 'none'; active = -1; }

    function escolher(it) {
      hidden.value = it.value;
      input.value = it.label;
      root.dataset.value = it.value;
      fechar();
      if (opts.onChange) opts.onChange(it);
    }

    function render(filtered) {
      shown = filtered;
      list.innerHTML = '';
      active = -1;
      if (!filtered.length) { fechar(); return; }
      filtered.forEach(function (it) {
        var li = document.createElement('li');
        li.className = 'cb-option';
        li.textContent = it.label;
        li.addEventListener('mousedown', function (e) { e.preventDefault(); escolher(it); });
        list.appendChild(li);
      });
      list.style.display = 'block';
    }

    function atualizar() {
      if (input.disabled) return;
      var q = input.value;
      Promise.resolve(opts.load(q)).then(function (data) {
        items = data || [];
        render(items.filter(function (it) { return norm(it.label).indexOf(norm(q)) !== -1; }));
      });
    }

    input.addEventListener('focus', atualizar);
    input.addEventListener('click', atualizar);
    input.addEventListener('input', function () {
      hidden.value = '';
      root.dataset.value = '';
      if (opts.onChange) opts.onChange(null);
      atualizar();
    });
    input.addEventListener('blur', function () { setTimeout(fechar, 150); });
    input.addEventListener('keydown', function (e) {
      var options = Array.prototype.slice.call(list.querySelectorAll('.cb-option'));
      if (e.key === 'ArrowDown') { e.preventDefault(); active = Math.min(active + 1, options.length - 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); active = Math.max(active - 1, 0); }
      else if (e.key === 'Enter') {
        if (active >= 0 && shown[active]) { e.preventDefault(); escolher(shown[active]); }
        return;
      } else if (e.key === 'Escape') { fechar(); return; }
      else { return; }
      options.forEach(function (o, i) { o.classList.toggle('active', i === active); });
    });

    return {
      setEnabled: function (on, placeholder) {
        input.disabled = !on;
        if (placeholder !== undefined) input.placeholder = placeholder;
        if (!on) { input.value = ''; hidden.value = ''; root.dataset.value = ''; }
      },
      setValue: function (value, label) {
        hidden.value = value;
        input.value = label;
        root.dataset.value = value;
      },
      reset: function () { input.value = ''; hidden.value = ''; root.dataset.value = ''; }
    };
  }

  function ufMunicipio(opts) {
    var ufRoot = document.querySelector(opts.ufSelector);
    var munRoot = document.querySelector(opts.munSelector);
    var ufSigla = '';
    var munCombo;

    var ufCombo = create(ufRoot, {
      load: function () {
        return getUfs().then(function (ufs) {
          return ufs.map(function (u) {
            return {
              value: opts.ufValueType === 'sigla' ? u.sigla : u.id,
              label: u.sigla + ' - ' + u.nome,
              sigla: u.sigla,
              id: u.id
            };
          });
        });
      },
      onChange: function (it) {
        ufSigla = it ? it.sigla : '';
        munCombo.reset();
        munCombo.setEnabled(!!it, it ? 'Digite para buscar o município...' : 'Selecione a UF primeiro');
        if (opts.onUfChange) opts.onUfChange(it);
      }
    });

    munCombo = create(munRoot, {
      load: function () {
        if (!ufSigla) return [];
        return getMunicipios(ufSigla).then(function (ms) {
          return ms.map(function (m) { return { value: m.id, label: m.nome }; });
        });
      },
      onChange: function (it) { if (opts.onMunChange) opts.onMunChange(it); }
    });
    munCombo.setEnabled(false, 'Selecione a UF primeiro');

    return {
      uf: ufCombo,
      mun: munCombo,
      getUfSigla: function () { return ufSigla; },
      getUfValue: function () { return ufRoot.dataset.value || ''; },
      getMunicipioValue: function () { return munRoot.dataset.value || ''; },
      setUf: function (value, label, sigla) {
        ufSigla = sigla || '';
        ufCombo.setValue(value, label);
        munCombo.reset();
        munCombo.setEnabled(!!sigla, sigla ? 'Digite para buscar o município...' : 'Selecione a UF primeiro');
      },
      setMunicipio: function (value, label) { munCombo.setValue(value, label); }
    };
  }

  window.Combobox = { create: create, ufMunicipio: ufMunicipio, getUfs: getUfs, getMunicipios: getMunicipios };
})();