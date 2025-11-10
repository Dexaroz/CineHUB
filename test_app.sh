#!/usr/bin/env bash
set -euo pipefail

# === Configura estos dos valores ===
API_URL="https://urtbepv1yg.execute-api.us-east-1.amazonaws.com/prod"  # ej: https://abc123.execute-api.us-east-1.amazonaws.com/prod
API_KEY="JQLHKe6iVw7QgPren56blS0JHnf4UDF2jTYc3ms4"

BASE="${API_URL}/movies"
HDRS=(-H "x-api-key: ${API_KEY}" -H "content-type: application/json" -H "accept: application/json")

# === Películas de prueba (sin jq) ===
MOVIES=(
'{"title":"Spirited Away","year":2001,"genre":"Animación, Fantasía","director":"Hayao Miyazaki","rating":9,"runtime":125,"poster":"https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg","synopsis":"Chihiro entra en un mundo mágico gobernado por espíritus."}'
'{"title":"The Matrix","year":1999,"genre":"Acción, Sci-Fi","director":"Lana & Lilly Wachowski","rating":9,"runtime":139,"poster":"https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg","synopsis":"Un hacker descubre la verdadera naturaleza de su realidad."}'
'{"title":"Parasite","year":2019,"genre":"Drama, Thriller","director":"Bong Joon Ho","rating":9,"runtime":132,"poster":"https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg","synopsis":"Una familia pobre se infiltra en la vida de una familia rica."}'
'{"title":"Pulp Fiction","year":1994,"genre":"Crimen","director":"Quentin Tarantino","rating":9,"runtime":154,"poster":"https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg","synopsis":"Historias entrelazadas de crimen y redención."}'
'{"title":"The Dark Knight","year":2008,"genre":"Acción, Crimen, Drama","director":"Christopher Nolan","rating":10,"runtime":152,"poster":"https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg","synopsis":"Batman se enfrenta al Joker en Gotham."}'
'{"title":"The Shawshank Redemption","year":1994,"genre":"Drama","director":"Frank Darabont","rating":10,"runtime":142,"poster":"https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg","synopsis":"Esperanza y amistad en Shawshank."}'
'{"title":"La La Land","year":2016,"genre":"Romance, Drama, Música","director":"Damien Chazelle","rating":8,"runtime":128,"poster":"https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg","synopsis":"Sueños en Los Ángeles."}'
'{"title":"Your Name","year":2016,"genre":"Animación, Romance, Fantasía","director":"Makoto Shinkai","rating":9,"runtime":112,"poster":"https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg","synopsis":"Adolescentes que intercambian cuerpos en sueños."}'
'{"title":"Avatar","year":2009,"genre":"Aventura, Sci-Fi","director":"James Cameron","rating":8,"runtime":162,"poster":"https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg","synopsis":"Humanos vs Na’vi en Pandora."}'
'{"title":"Interstellar","year":2014,"genre":"Sci-Fi","director":"Christopher Nolan","rating":9,"runtime":169,"poster":"https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg","synopsis":"Viaje a través de un agujero de gusano."}'
)

# === Helpers (sin jq) ===
extract_id() {
  # Extrae la primera ocurrencia de "id": N del JSON de respuesta
  sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' | head -n1
}

# === 1) Crear muchas películas ===
echo "== Creando películas =="
IDS=()
for payload in "${MOVIES[@]}"; do
  RESP="$(curl -s -X POST "${BASE}" "${HDRS[@]}" -d "${payload}")"
  echo "RESP: ${RESP}"
  ID="$(printf '%s\n' "$RESP" | extract_id || true)"
  if [[ -n "${ID:-}" ]]; then
    IDS+=("$ID")
  fi
done

# === 2) Listar todas ===
echo
echo "== GET /movies =="
curl -s "${BASE}" "${HDRS[@]}"
echo

# === 3) Obtener por ID (primera creada) ===
if [[ ${#IDS[@]} -gt 0 ]]; then
  ONE_ID="${IDS[0]}"
  echo
  echo "== GET /movies/${ONE_ID} =="
  curl -s "${BASE}/${ONE_ID}" "${HDRS[@]}"
  echo
fi

# === 4) Actualizar una (segunda si existe; si no, la primera) ===
TARGET_ID="${IDS[1]:-${IDS[0]:-}}"
if [[ -n "${TARGET_ID:-}" ]]; then
  echo
  echo "== PUT /movies/${TARGET_ID} (rating/runtime/title) =="
  curl -s -X PUT "${BASE}/${TARGET_ID}" "${HDRS[@]}" \
    -d '{"rating":10,"runtime":180,"title":"(UPDATED)"}'
  echo
  echo "== GET /movies/${TARGET_ID} (ver cambios) =="
  curl -s "${BASE}/${TARGET_ID}" "${HDRS[@]}"
  echo
fi

# === 5) Borrar una (la última creada; si no, la primera) ===
DEL_ID="${IDS[-1]:-${IDS[0]:-}}"
if [[ -n "${DEL_ID:-}" ]]; then
  echo
  echo "== DELETE /movies/${DEL_ID} =="
  curl -i -X DELETE "${BASE}/${DEL_ID}" "${HDRS[@]}" | sed -n '1,10p'
fi

# === 6) Listar nuevamente ===
echo
echo "== GET /movies (tras update/delete) =="
curl -s "${BASE}" "${HDRS[@]}"
echo
echo "Hecho."
