enum Engine {
  defaultEngine,
  openai,
}

extension EngineQuery on Engine {
  String get queryValue => this == Engine.openai ? 'openai' : 'default';
}
