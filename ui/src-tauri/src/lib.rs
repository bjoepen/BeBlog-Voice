use serde_json::{json, Value};
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::State;
use tauri_plugin_dialog::DialogExt;

struct ProjectState(Mutex<Option<Value>>);

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn call_python(request: Value) -> Result<Value, String> {
    let root = repo_root();
    let script = root.join("scripts/ui-project-bridge.py");

    let mut child = Command::new("python3")
        .arg(script)
        .current_dir(&root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|error| format!("Python bridge could not start: {error}"))?;

    let payload = serde_json::to_vec(&request)
        .map_err(|error| format!("Bridge request could not be encoded: {error}"))?;

    child
        .stdin
        .as_mut()
        .ok_or_else(|| "Python bridge stdin unavailable".to_string())?
        .write_all(&payload)
        .map_err(|error| format!("Bridge request could not be written: {error}"))?;

    let output = child
        .wait_with_output()
        .map_err(|error| format!("Python bridge failed: {error}"))?;

    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }

    serde_json::from_slice(&output.stdout)
        .map_err(|error| format!("Bridge response could not be decoded: {error}"))
}

fn update_state(state: &State<'_, ProjectState>, response: &Value) -> Result<(), String> {
    let project = response
        .get("project")
        .cloned()
        .ok_or_else(|| "Bridge response has no project".to_string())?;

    *state
        .0
        .lock()
        .map_err(|_| "Project state lock failed".to_string())? = Some(project);
    Ok(())
}

fn current_project(state: &State<'_, ProjectState>) -> Result<Value, String> {
    state
        .0
        .lock()
        .map_err(|_| "Project state lock failed".to_string())?
        .clone()
        .ok_or_else(|| "Project state is not loaded".to_string())
}

#[tauri::command]
fn load_project_state(state: State<'_, ProjectState>) -> Result<Value, String> {
    let response = call_python(json!({ "action": "load" }))?;
    update_state(&state, &response)?;
    Ok(response["view"].clone())
}

#[tauri::command]
async fn open_project_file(
    app: tauri::AppHandle,
    state: State<'_, ProjectState>,
) -> Result<Option<Value>, String> {
    let path = app
        .dialog()
        .file()
        .add_filter("BeBlog Voice", &["bbv"])
        .pick_file()
        .await;

    let Some(path) = path else {
        return Ok(None);
    };

    let path = path
        .as_path()
        .ok_or_else(|| "Selected project is not a local file".to_string())?;

    let response = call_python(json!({
        "action": "open-file",
        "path": path.to_string_lossy(),
    }))?;
    update_state(&state, &response)?;
    Ok(Some(response["view"].clone()))
}

#[tauri::command]
async fn save_project_file(
    app: tauri::AppHandle,
    state: State<'_, ProjectState>,
) -> Result<bool, String> {
    let project = current_project(&state)?;
    let path = app
        .dialog()
        .file()
        .add_filter("BeBlog Voice", &["bbv"])
        .set_file_name("BeBlog-Voice.bbv")
        .save_file()
        .await;

    let Some(path) = path else {
        return Ok(false);
    };

    let path = path
        .as_path()
        .ok_or_else(|| "Selected project is not a local file".to_string())?;

    let response = call_python(json!({
        "action": "save-file",
        "path": path.to_string_lossy(),
        "project": project,
    }))?;
    update_state(&state, &response)?;
    Ok(true)
}

#[tauri::command]
fn sync_manuscript(manuscript: String, state: State<'_, ProjectState>) -> Result<Value, String> {
    let project = current_project(&state)?;
    let response = call_python(json!({
        "action": "sync",
        "project": project,
        "manuscript": manuscript,
    }))?;
    update_state(&state, &response)?;
    Ok(response["view"].clone())
}

#[tauri::command]
fn set_unit_voice(
    unit_id: String,
    voice_id: String,
    state: State<'_, ProjectState>,
) -> Result<Value, String> {
    let project = current_project(&state)?;
    let response = call_python(json!({
        "action": "voice",
        "project": project,
        "unitId": unit_id,
        "voiceId": voice_id,
    }))?;
    update_state(&state, &response)?;
    Ok(response["view"].clone())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(ProjectState(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            load_project_state,
            open_project_file,
            save_project_file,
            sync_manuscript,
            set_unit_voice,
        ])
        .run(tauri::generate_context!())
        .expect("error while running BeBlog Voice");
}
