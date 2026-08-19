/// Storage service interface for local state and token persistence.
class StorageService {
  static final Map<String, String> _inMemoryStorage = {};

  Future<void> write(String key, String value) async {
    _inMemoryStorage[key] = value;
  }

  Future<String?> read(String key) async {
    return _inMemoryStorage[key];
  }

  Future<void> delete(String key) async {
    _inMemoryStorage.remove(key);
  }

  Future<void> clearAll() async {
    _inMemoryStorage.clear();
  }
}
