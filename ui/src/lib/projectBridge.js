import { invoke } from "@tauri-apps/api/core";

export const projectBridge = {
  loadProjectState() {
    return invoke("load_project_state");
  },

  openProjectFile() {
    return invoke("open_project_file");
  },

  saveProjectFile() {
    return invoke("save_project_file");
  },

  syncManuscript(manuscript) {
    return invoke("sync_manuscript", { manuscript });
  },

  setUnitVoice(unitId, voiceId) {
    return invoke("set_unit_voice", { unitId, voiceId });
  },

  renderProjectUnit(unitId, previousAudio = null) {
    return invoke("render_project_unit", { unitId, previousAudio });
  },
};

export const loadProjectState = () => projectBridge.loadProjectState();
export const openProjectFile = () => projectBridge.openProjectFile();
export const saveProjectFile = () => projectBridge.saveProjectFile();
export const syncManuscript = (manuscript) => projectBridge.syncManuscript(manuscript);
export const setUnitVoice = (unitId, voiceId) => projectBridge.setUnitVoice(unitId, voiceId);
export const renderProjectUnit = (unitId, previousAudio = null) =>
  projectBridge.renderProjectUnit(unitId, previousAudio);
