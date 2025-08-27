// Almacenamiento simulado (en un caso real, esto vendría de una API)
let marcas = JSON.parse(localStorage.getItem('marcas')) || [];
let modelos = JSON.parse(localStorage.getItem('modelos')) || [];
let colores = JSON.parse(localStorage.getItem('colores')) || [];
let tallas = JSON.parse(localStorage.getItem('tallas')) || [];
let productos = JSON.parse(localStorage.getItem('productos')) || [];

// Elementos DOM
const alertBox = document.getElementById('alert-box');

// Mostrar alerta
function showAlert(message, type = 'success') {
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type}`;
    alertBox.style.display = 'block';
    
    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 3000);
}

// Navegación por pestañas
document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remover clase active de todos los links y contenidos
        document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Agregar clase active al link clickeado
        link.classList.add('active');
        
        // Mostrar el contenido correspondiente
        const target = link.getAttribute('href');
        document.querySelector(target).classList.add('active');
        
        // Si es la pestaña de modelos, cargar las marcas en el select
        if (target === '#modelos') {
            loadMarcasInSelect('modelo-marca');
        }
        
        // Si es la pestaña de productos, cargar los selects
        if (target === '#productos') {
            loadMarcasInSelect('producto-marca');
            loadColoresInSelect('producto-color');
            loadTallasInSelect('producto-talla');
        }
    });
});

// Cargar marcas en un select
function loadMarcasInSelect(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Seleccione una marca</option>';
    
    marcas.forEach(marca => {
        if (marca.activo !== false) {
            const option = document.createElement('option');
            option.value = marca.id;
            option.textContent = marca.nombre;
            select.appendChild(option);
        }
    });
    
    // Si es el selector de marcas para productos, cargar modelos cuando cambie
    if (selectId === 'producto-marca') {
        select.addEventListener('change', function() {
            loadModelosByMarca(this.value, 'producto-modelo');
        });
    }
}

// Cargar modelos por marca
function loadModelosByMarca(marcaId, selectId) {
    const select = document.getElementById(selectId);
    
    if (!marcaId) {
        select.innerHTML = '<option value="">Primero seleccione una marca</option>';
        select.disabled = true;
        return;
    }
    
    select.innerHTML = '<option value="">Seleccione un modelo</option>';
    select.disabled = false;
    
    modelos.forEach(modelo => {
        if (modelo.marcaId == marcaId && modelo.activo !== false) {
            const option = document.createElement('option');
            option.value = modelo.id;
            option.textContent = modelo.nombre;
            select.appendChild(option);
        }
    });
}

// Cargar colores en un select
function loadColoresInSelect(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Seleccione un color</option>';
    
    colores.forEach(color => {
        if (color.activo !== false) {
            const option = document.createElement('option');
            option.value = color.id;
            option.textContent = color.nombre;
            select.appendChild(option);
        }
    });
}

// Cargar tallas en un select
function loadTallasInSelect(selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Seleccione una talla</option>';
    
    tallas.forEach(talla => {
        const option = document.createElement('option');
        option.value = talla.id;
        option.textContent = `${talla.valor} (${getTipoTallaText(talla.tipo)})`;
        select.appendChild(option);
    });
}

// Obtener texto para tipo de talla
function getTipoTallaText(tipo) {
    switch(tipo) {
        case 'NUM': return 'Numérica';
        case 'LET': return 'Letras';
        case 'EUR': return 'Europea';
        case 'USA': return 'Americana';
        default: return tipo;
    }
}

// Generar ID único
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Guardar marcas en localStorage
function saveMarcas() {
    localStorage.setItem('marcas', JSON.stringify(marcas));
    renderMarcasTable();
}

// Guardar modelos en localStorage
function saveModelos() {
    localStorage.setItem('modelos', JSON.stringify(modelos));
    renderModelosTable();
}

// Guardar colores en localStorage
function saveColores() {
    localStorage.setItem('colores', JSON.stringify(colores));
    renderColoresTable();
}

// Guardar tallas en localStorage
function saveTallas() {
    localStorage.setItem('tallas', JSON.stringify(tallas));
    renderTallasTable();
}

// Guardar productos en localStorage
function saveProductos() {
    localStorage.setItem('productos', JSON.stringify(productos));
    renderProductosTable();
}

// Renderizar tabla de marcas
function renderMarcasTable() {
    const tbody = document.getElementById('tabla-marcas');
    tbody.innerHTML = '';
    
    marcas.forEach(marca => {
        if (marca.activo !== false) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${marca.id}</td>
                <td>${marca.nombre}</td>
                <td>${marca.descripcion || ''}</td>
                <td class="actions">
                    <button class="btn-delete" onclick="deleteMarca('${marca.id}')">Eliminar</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Renderizar tabla de modelos
function renderModelosTable() {
    const tbody = document.getElementById('tabla-modelos');
    tbody.innerHTML = '';
    
    modelos.forEach(modelo => {
        if (modelo.activo !== false) {
            const marca = marcas.find(m => m.id === modelo.marcaId);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${modelo.id}</td>
                <td>${marca ? marca.nombre : 'N/A'}</td>
                <td>${modelo.nombre}</td>
                <td>${modelo.descripcion || ''}</td>
                <td class="actions">
                    <button class="btn-delete" onclick="deleteModelo('${modelo.id}')">Eliminar</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Renderizar tabla de colores
function renderColoresTable() {
    const tbody = document.getElementById('tabla-colores');
    tbody.innerHTML = '';
    
    colores.forEach(color => {
        if (color.activo !== false) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${color.id}</td>
                <td>${color.nombre}</td>
                <td>${color.codigoHex || ''}</td>
                <td class="actions">
                    <button class="btn-delete" onclick="deleteColor('${color.id}')">Eliminar</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Renderizar tabla de tallas
function renderTallasTable() {
    const tbody = document.getElementById('tabla-tallas');
    tbody.innerHTML = '';
    
    tallas.forEach(talla => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${talla.id}</td>
            <td>${talla.valor}</td>
            <td>${getTipoTallaText(talla.tipo)}</td>
            <td class="actions">
                <button class="btn-delete" onclick="deleteTalla('${talla.id}')">Eliminar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Renderizar tabla de productos
function renderProductosTable() {
    const tbody = document.getElementById('tabla-productos');
    tbody.innerHTML = '';
    
    productos.forEach(producto => {
        if (producto.activo !== false) {
            const modelo = modelos.find(m => m.id === producto.modeloId);
            const marca = modelo ? marcas.find(m => m.id === modelo.marcaId) : null;
            const color = colores.find(c => c.id === producto.colorId);
            const talla = tallas.find(t => t.id === producto.tallaId);
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${producto.sku}</td>
                <td>${marca ? marca.nombre : 'N/A'}</td>
                <td>${modelo ? modelo.nombre : 'N/A'}</td>
                <td>${color ? color.nombre : 'N/A'}</td>
                <td>${talla ? `${talla.valor} (${getTipoTallaText(talla.tipo)})` : 'N/A'}</td>
                <td>$${producto.precio.toFixed(2)}</td>
                <td>${producto.stock}</td>
                <td class="actions">
                    <button class="btn-delete" onclick="deleteProducto('${producto.id}')">Eliminar</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Eliminar marca
function deleteMarca(id) {
    if (confirm('¿Está seguro de eliminar esta marca?')) {
        // Verificar si hay modelos asociados
        const modelosAsociados = modelos.filter(m => m.marcaId === id && m.activo !== false);
        if (modelosAsociados.length > 0) {
            showAlert('No se puede eliminar la marca porque tiene modelos asociados', 'error');
            return;
        }
        
        // Marcar como inactivo en lugar de eliminar
        const index = marcas.findIndex(m => m.id === id);
        if (index !== -1) {
            marcas[index].activo = false;
            saveMarcas();
            showAlert('Marca eliminada correctamente');
        }
    }
}

// Eliminar modelo
function deleteModelo(id) {
    if (confirm('¿Está seguro de eliminar este modelo?')) {
        // Verificar si hay productos asociados
        const productosAsociados = productos.filter(p => p.modeloId === id && p.activo !== false);
        if (productosAsociados.length > 0) {
            showAlert('No se puede eliminar el modelo porque tiene productos asociados', 'error');
            return;
        }
        
        // Marcar como inactivo en lugar de eliminar
        const index = modelos.findIndex(m => m.id === id);
        if (index !== -1) {
            modelos[index].activo = false;
            saveModelos();
            showAlert('Modelo eliminado correctamente');
        }
    }
}

// Eliminar color
function deleteColor(id) {
    if (confirm('¿Está seguro de eliminar este color?')) {
        // Verificar si hay productos asociados
        const productosAsociados = productos.filter(p => p.colorId === id && p.activo !== false);
        if (productosAsociados.length > 0) {
            showAlert('No se puede eliminar el color porque tiene productos asociados', 'error');
            return;
        }
        
        // Marcar como inactivo en lugar de eliminar
        const index = colores.findIndex(c => c.id === id);
        if (index !== -1) {
            colores[index].activo = false;
            saveColores();
            showAlert('Color eliminado correctamente');
        }
    }
}

// Eliminar talla
function deleteTalla(id) {
    if (confirm('¿Está seguro de eliminar esta talla?')) {
        // Verificar si hay productos asociados
        const productosAsociados = productos.filter(p => p.tallaId === id && p.activo !== false);
        if (productosAsociados.length > 0) {
            showAlert('No se puede eliminar la talla porque tiene productos asociados', 'error');
            return;
        }
        
        // Eliminar la talla
        const index = tallas.findIndex(t => t.id === id);
        if (index !== -1) {
            tallas.splice(index, 1);
            saveTallas();
            showAlert('Talla eliminada correctamente');
        }
    }
}

// Eliminar producto
function deleteProducto(id) {
    if (confirm('¿Está seguro de eliminar este producto?')) {
        // Marcar como inactivo en lugar de eliminar
        const index = productos.findIndex(p => p.id === id);
        if (index !== -1) {
            productos[index].activo = false;
            saveProductos();
            showAlert('Producto eliminado correctamente');
        }
    }
}

// Formulario para agregar marca
document.getElementById('form-marca').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const nombre = document.getElementById('marca-nombre').value;
    const descripcion = document.getElementById('marca-descripcion').value;
    
    const nuevaMarca = {
        id: generateId(),
        nombre,
        descripcion,
        fechaCreacion: new Date().toISOString(),
        activo: true
    };
    
    marcas.push(nuevaMarca);
    saveMarcas();
    
    this.reset();
    showAlert('Marca agregada correctamente');
});

// Formulario para agregar modelo
document.getElementById('form-modelo').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const marcaId = document.getElementById('modelo-marca').value;
    const nombre = document.getElementById('modelo-nombre').value;
    const descripcion = document.getElementById('modelo-descripcion').value;
    
    const nuevoModelo = {
        id: generateId(),
        marcaId,
        nombre,
        descripcion,
        fechaCreacion: new Date().toISOString(),
        activo: true
    };
    
    modelos.push(nuevoModelo);
    saveModelos();
    
    this.reset();
    showAlert('Modelo agregado correctamente');
});

// Formulario para agregar color
document.getElementById('form-color').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const nombre = document.getElementById('color-nombre').value;
    const codigoHex = document.getElementById('color-codigo').value;
    
    const nuevoColor = {
        id: generateId(),
        nombre,
        codigoHex,
        activo: true
    };
    
    colores.push(nuevoColor);
    saveColores();
    
    this.reset();
    showAlert('Color agregado correctamente');
});

// Formulario para agregar talla
document.getElementById('form-talla').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const valor = document.getElementById('talla-valor').value;
    const tipo = document.getElementById('talla-tipo').value;
    
    const nuevaTalla = {
        id: generateId(),
        valor,
        tipo
    };
    
    tallas.push(nuevaTalla);
    saveTallas();
    
    this.reset();
    showAlert('Talla agregada correctamente');
});

// Formulario para agregar producto
document.getElementById('form-producto').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const modeloId = document.getElementById('producto-modelo').value;
    const colorId = document.getElementById('producto-color').value;
    const tallaId = document.getElementById('producto-talla').value;
    const sku = document.getElementById('producto-sku').value;
    const precio = parseFloat(document.getElementById('producto-precio').value);
    const precioDescuento = document.getElementById('producto-precio-descuento').value ? 
        parseFloat(document.getElementById('producto-precio-descuento').value) : null;
    const stock = parseInt(document.getElementById('producto-stock').value);
    
    // Verificar si ya existe un producto con la misma combinación
    const existeProducto = productos.find(p => 
        p.modeloId === modeloId && 
        p.colorId === colorId && 
        p.tallaId === tallaId &&
        p.activo !== false
    );
    
    if (existeProducto) {
        showAlert('Ya existe un producto con esta combinación de modelo, color y talla', 'error');
        return;
    }
    
    const nuevoProducto = {
        id: generateId(),
        modeloId,
        colorId,
        tallaId,
        sku,
        precio,
        precioDescuento,
        stock,
        fechaCreacion: new Date().toISOString(),
        activo: true
    };
    
    productos.push(nuevoProducto);
    saveProductos();
    
    this.reset();
    // Resetear también el selector de modelos
    document.getElementById('producto-modelo').innerHTML = '<option value="">Primero seleccione una marca</option>';
    document.getElementById('producto-modelo').disabled = true;
    showAlert('Producto agregado correctamente');
});

// Botón para ver catálogo público
document.getElementById('btn-view-catalog').addEventListener('click', function() {
    alert('En una implementación real, esto abriría la vista pública del catálogo');
});

// Inicializar la aplicación
function init() {
    // Cargar datos en las tablas
    renderMarcasTable();
    renderModelosTable();
    renderColoresTable();
    renderTallasTable();
    renderProductosTable();
    
    // Cargar marcas en el select de modelos
    loadMarcasInSelect('modelo-marca');
}

// Iniciar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
