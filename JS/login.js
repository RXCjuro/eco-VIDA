function iniciarSesionReal(email, password) {

    let credenciales = {
        correo: email.trim().toLowerCase(),
        contrasena: password
    };

    fetch(`${BASE_RENDER_URL}/api/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(credenciales)

    })

    .then(function (response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                throw new Error(
                    data.error || "Fallo en la autenticación"
                );
            }
            return data;
        });
    })

    .then(function (data) {
        console.log("Login correcto");
        localStorage.setItem(
            "authToken",
            data.token
        );
        localStorage.setItem(
            "usuarioLogueado",
            JSON.stringify(data.usuario)
        );
        alert(
            "🔑 ¡Bienvenido, " +
            data.usuario.nombre +
            "!"
        );

        window.location.href = "index.html";})

    .catch(function (error) {
        console.error(
            "Error de autenticación:",
            error
        );
        alert(
            "❌ Error de acceso: " +
            error.message
        );
    });
}

function manejarFormularioLogin(evento) {
    evento.preventDefault();
    let email =
        document.getElementById("loginEmail").value;
    let contrasena =
        document.getElementById("loginPassword").value;
    iniciarSesionReal(
        email,
        contrasena
    );
}