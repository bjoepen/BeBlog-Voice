import { invoke } from "@tauri-apps/api/core";

export const projectBridge = {
  loadProjectState() { return invoke("load_project_state"); },
  openProjectFile() { return invoke("open_project_file"); },
  saveProjectFile(audioByUnit = {}) { return invoke("save_project_file", { audioByUnit }); },
  syncManuscript(manuscript, audioByUnit = {}) { return invoke("sync_manuscript", { manuscript, audioByUnit }); },
  setUnitVoice(unitId, voiceId, audioByUnit = {}) { return invoke("set_unit_voice", { unitId, voiceId, audioByUnit }); },
  renderProjectUnit(unitId, previousAudio = null) { return invoke("render_project_unit", { unitId, previousAudio }); },
  playUnitAudio(unitId, audioPath) { return invoke("play_unit_audio", { unitId, audioPath }); },
  stopUnitAudio(unitId) { return invoke("stop_unit_audio", { unitId }); },
  isUnitAudioPlaying(unitId) { return invoke("is_unit_audio_playing", { unitId }); },
};

export const loadProjectState = () => projectBridge.loadProjectState();
export const openProjectFile = () => projectBridge.openProjectFile();
export const saveProjectFile = (audioByUnit = {}) => projectBridge.saveProjectFile(audioByUnit);
export const syncManuscript = (manuscript, audioByUnit = {}) => projectBridge.syncManuscript(manuscript, audioByUnit);
export const setUnitVoice = (unitId, voiceId, audioByUnit = {}) => projectBridge.setUnitVoice(unitId, voiceId, audioByUnit);
export const renderProjectUnit = (unitId, previousAudio = null) => projectBridge.renderProjectUnit(unitId, previousAudio);
export const playUnitAudio = (unitId, audioPath) => projectBridge.playUnitAudio(unitId, audioPath);
export const stopUnitAudio = (unitId) => projectBridge.stopUnitAudio(unitId);
export const isUnitAudioPlaying = (unitId) => projectBridge.isUnitAudioPlaying(unitId);
