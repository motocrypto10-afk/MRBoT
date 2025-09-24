import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Switch,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

interface UserSettings {
  id: string;
  openai_api_key?: string;
  preferred_language: string;
  auto_delete_days?: number;
  cloud_sync_enabled: boolean;
  privacy_mode: boolean;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function SettingsScreen() {
  const [settings, setSettings] = useState<UserSettings>({
    id: '',
    preferred_language: 'en',
    cloud_sync_enabled: true,
    privacy_mode: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
      Alert.alert('Error', 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Settings saved successfully');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      Alert.alert('Error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const updateSetting = (key: keyof UserSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ta', name: 'Tamil' },
    { code: 'hi', name: 'Hindi' },
    { code: 'fr', name: 'French' },
    { code: 'it', name: 'Italian' },
  ];

  const showLanguageSelector = () => {
    const options = languages.map(lang => ({
      text: lang.name,
      onPress: () => updateSetting('preferred_language', lang.code),
    }));
    options.push({ text: 'Cancel', onPress: () => {} });

    Alert.alert('Select Language', 'Choose your preferred language:', options);
  };

  const showDeleteOptions = () => {
    const options = [
      { text: 'Never', onPress: () => updateSetting('auto_delete_days', null) },
      { text: '7 days', onPress: () => updateSetting('auto_delete_days', 7) },
      { text: '30 days', onPress: () => updateSetting('auto_delete_days', 30) },
      { text: '90 days', onPress: () => updateSetting('auto_delete_days', 90) },
      { text: 'Cancel', onPress: () => {} },
    ];

    Alert.alert('Auto Delete', 'Choose when to automatically delete recordings:', options);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading settings...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* API Configuration Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>API Configuration</Text>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>OpenAI API Key</Text>
            <Text style={styles.settingDescription}>
              Optional: Use your own OpenAI key for transcription
            </Text>
            <TextInput
              style={styles.textInput}
              placeholder="sk-..."
              value={settings.openai_api_key || ''}
              onChangeText={(text) => updateSetting('openai_api_key', text)}
              secureTextEntry
            />
            <Text style={styles.helpText}>
              Leave empty to use Emergent LLM key (default)
            </Text>
          </View>
        </View>

        {/* Language Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Language & Transcription</Text>
          
          <TouchableOpacity style={styles.settingItem} onPress={showLanguageSelector}>
            <Text style={styles.settingLabel}>Preferred Language</Text>
            <View style={styles.settingValue}>
              <Text style={styles.settingValueText}>
                {languages.find(l => l.code === settings.preferred_language)?.name || 'English'}
              </Text>
              <Ionicons name="chevron-forward" size={16} color="#8E8E93" />
            </View>
          </TouchableOpacity>
        </View>

        {/* Privacy Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Privacy & Data</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Cloud Sync</Text>
                <Text style={styles.settingDescription}>
                  Sync recordings to cloud for backup
                </Text>
              </View>
              <Switch
                value={settings.cloud_sync_enabled}
                onValueChange={(value) => updateSetting('cloud_sync_enabled', value)}
              />
            </View>
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Privacy Mode</Text>
                <Text style={styles.settingDescription}>
                  Keep recordings local only
                </Text>
              </View>
              <Switch
                value={settings.privacy_mode}
                onValueChange={(value) => updateSetting('privacy_mode', value)}
              />
            </View>
          </View>

          <TouchableOpacity style={styles.settingItem} onPress={showDeleteOptions}>
            <Text style={styles.settingLabel}>Auto Delete</Text>
            <View style={styles.settingValue}>
              <Text style={styles.settingValueText}>
                {settings.auto_delete_days 
                  ? `${settings.auto_delete_days} days` 
                  : 'Never'}
              </Text>
              <Ionicons name="chevron-forward" size={16} color="#8E8E93" />
            </View>
          </TouchableOpacity>
        </View>

        {/* Integrations Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Integrations</Text>
          
          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.integrationRow}>
              <Ionicons name="logo-google" size={24} color="#4285f4" />
              <View style={styles.integrationInfo}>
                <Text style={styles.settingLabel}>Google Drive</Text>
                <Text style={styles.settingDescription}>Export to Google Drive</Text>
              </View>
              <Text style={styles.connectButton}>Connect</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.integrationRow}>
              <Ionicons name="document-text" size={24} color="#000000" />
              <View style={styles.integrationInfo}>
                <Text style={styles.settingLabel}>Notion</Text>
                <Text style={styles.settingDescription}>Save to Notion workspace</Text>
              </View>
              <Text style={styles.connectButton}>Connect</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.integrationRow}>
              <Ionicons name="briefcase" size={24} color="#ff6b35" />
              <View style={styles.integrationInfo}>
                <Text style={styles.settingLabel}>Zoho Projects</Text>
                <Text style={styles.settingDescription}>Sync tasks to Zoho</Text>
              </View>
              <Text style={styles.connectButton}>Connect</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={saveSettings}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Saving...' : 'Save Settings'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#8E8E93',
  },
  scrollContainer: {
    padding: 16,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#000',
    marginBottom: 16,
  },
  settingItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#8E8E93',
  },
  settingValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingValueText: {
    fontSize: 16,
    color: '#007AFF',
    marginRight: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginTop: 8,
    backgroundColor: '#FFFFFF',
  },
  helpText: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
  },
  integrationRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  integrationInfo: {
    flex: 1,
    marginLeft: 12,
  },
  connectButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  saveButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  saveButtonDisabled: {
    backgroundColor: '#8E8E93',
  },
  saveButtonText: {
    fontSize: 18,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});