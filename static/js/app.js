/* =========================================================================
   Club de Motociclistas - interacciones del navegador
   Sin dependencias. Todo es opcional: la pagina funciona sin este archivo.
   ========================================================================= */
(function () {
    "use strict";

    /* ------------------------------------------------------------------
       Tema claro / oscuro
       ------------------------------------------------------------------ */
    var CLAVE_TEMA = "club-moto-tema";

    function aplicarTema(tema) {
        document.documentElement.setAttribute("data-tema", tema);
        try {
            localStorage.setItem(CLAVE_TEMA, tema);
        } catch (error) {
            /* modo privado: se ignora */
        }
    }

    function iniciarTema() {
        var guardado = null;
        try {
            guardado = localStorage.getItem(CLAVE_TEMA);
        } catch (error) {
            guardado = null;
        }
        var preferido = window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "oscuro"
            : "claro";
        aplicarTema(guardado || preferido);

        document.addEventListener("click", function (evento) {
            var boton = evento.target.closest("[data-tema-boton]");
            if (!boton) {
                return;
            }
            evento.preventDefault();
            var actual = document.documentElement.getAttribute("data-tema");
            aplicarTema(actual === "oscuro" ? "claro" : "oscuro");
        });
    }

    /* ------------------------------------------------------------------
       Menu lateral en movil
       ------------------------------------------------------------------ */
    function iniciarMenu() {
        var lateral = document.querySelector(".lateral");
        var boton = document.querySelector("[data-menu-boton]");
        var velo = document.querySelector(".velo");
        if (!lateral || !boton) {
            return;
        }

        function alternar(abrir) {
            lateral.classList.toggle("abierta", abrir);
            if (velo) {
                velo.classList.toggle("visible", abrir);
            }
            document.body.style.overflow = abrir ? "hidden" : "";
        }

        boton.addEventListener("click", function () {
            alternar(!lateral.classList.contains("abierta"));
        });

        if (velo) {
            velo.addEventListener("click", function () {
                alternar(false);
            });
        }

        document.addEventListener("keydown", function (evento) {
            if (evento.key === "Escape") {
                alternar(false);
            }
        });

        lateral.addEventListener("click", function (evento) {
            if (evento.target.closest("a") && window.innerWidth <= 1100) {
                alternar(false);
            }
        });
    }

    /* ------------------------------------------------------------------
       Filtro de tablas
       ------------------------------------------------------------------ */
    function iniciarFiltros() {
        var entradas = document.querySelectorAll("[data-filtro]");
        Array.prototype.forEach.call(entradas, function (entrada) {
            var zona = document.getElementById(entrada.getAttribute("data-filtro"));
            if (!zona) {
                return;
            }
            entrada.addEventListener("input", function () {
                var texto = entrada.value.trim().toLowerCase();
                var esTabla = zona.tagName === "TABLE";
                var elementos = esTabla
                    ? zona.querySelectorAll("tbody tr")
                    : zona.querySelectorAll("[data-fila]");
                var visibles = 0;
                Array.prototype.forEach.call(elementos, function (elemento) {
                    if (elemento.hasAttribute("data-vacio")) {
                        return;
                    }
                    var coincide = texto === "" || elemento.textContent.toLowerCase().indexOf(texto) !== -1;
                    elemento.style.display = coincide ? "" : "none";
                    if (coincide) {
                        visibles += 1;
                    }
                });
                var marcador = document.querySelector("[data-filtro-vacio]");
                if (marcador) {
                    marcador.classList.toggle("oculto", visibles !== 0);
                }
            });
        });
    }

    /* ------------------------------------------------------------------
       Confirmacion de borrado
       ------------------------------------------------------------------ */
    function iniciarConfirmaciones() {
        document.addEventListener("submit", function (evento) {
            var formulario = evento.target.closest("form[data-confirmar]");
            if (!formulario) {
                return;
            }
            var mensaje = formulario.getAttribute("data-confirmar");
            if (!window.confirm(mensaje)) {
                evento.preventDefault();
            }
        });
    }

    /* ------------------------------------------------------------------
       Avisos: se ocultan solos
       ------------------------------------------------------------------ */
    function iniciarAvisos() {
        var avisos = document.querySelectorAll(".aviso");
        Array.prototype.forEach.call(avisos, function (aviso) {
            window.setTimeout(function () {
                aviso.style.transition = "opacity 400ms, transform 400ms";
                aviso.style.opacity = "0";
                aviso.style.transform = "translateY(-6px)";
                window.setTimeout(function () {
                    aviso.remove();
                }, 420);
            }, 6000);
        });
    }

    /* ------------------------------------------------------------------
       Año en el pie de pagina
       ------------------------------------------------------------------ */
    function iniciarAnio() {
        var nodos = document.querySelectorAll("[data-anio]");
        Array.prototype.forEach.call(nodos, function (nodo) {
            nodo.textContent = String(new Date().getFullYear());
        });
    }

    /* ------------------------------------------------------------------
       Arranque
       ------------------------------------------------------------------ */
    function iniciar() {
        iniciarTema();
        iniciarMenu();
        iniciarFiltros();
        iniciarConfirmaciones();
        iniciarAvisos();
        iniciarAnio();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar);
    } else {
        iniciar();
    }
})();
