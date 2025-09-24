import React from 'react';
import { StyleSheet, Platform } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

// Import screens
import SummaryFeedScreen from './screens/SummaryFeedScreen';
import TasksScreen from './screens/TasksScreen';
import MomScreen from './screens/MomScreen';
import MessagesScreen from './screens/MessagesScreen';
import SettingsScreen from './screens/SettingsScreen';
import RecordingScreen from './screens/RecordingScreen';

const Tab = createBottomTabNavigator();

export default function Index() {
  return (
    <SafeAreaProvider>
      <NavigationContainer independent={true}>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName: keyof typeof Ionicons.glyphMap;

              if (route.name === 'Summary') {
                iconName = focused ? 'home' : 'home-outline';
              } else if (route.name === 'Tasks') {
                iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
              } else if (route.name === 'MoM') {
                iconName = focused ? 'document-text' : 'document-text-outline';
              } else if (route.name === 'Messages') {
                iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
              } else if (route.name === 'Settings') {
                iconName = focused ? 'settings' : 'settings-outline';
              } else if (route.name === 'Record') {
                iconName = 'mic';
              } else {
                iconName = 'ellipse-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#007AFF',
            tabBarInactiveTintColor: '#8E8E93',
            tabBarStyle: {
              backgroundColor: '#FFFFFF',
              borderTopWidth: 0.5,
              borderTopColor: '#E5E5EA',
              paddingBottom: Platform.OS === 'ios' ? 25 : 8,
              paddingTop: 8,
              height: Platform.OS === 'ios' ? 85 : 65,
              shadowColor: '#000',
              shadowOffset: {
                width: 0,
                height: -2,
              },
              shadowOpacity: 0.1,
              shadowRadius: 8,
              elevation: 10,
            },
            tabBarItemStyle: {
              paddingVertical: 4,
            },
            tabBarLabelStyle: {
              fontSize: 11,
              fontWeight: '500',
              marginTop: 2,
            },
            headerStyle: {
              backgroundColor: '#FFFFFF',
              borderBottomWidth: 0.5,
              borderBottomColor: '#E5E5EA',
              shadowColor: '#000',
              shadowOffset: {
                width: 0,
                height: 1,
              },
              shadowOpacity: 0.05,
              shadowRadius: 4,
              elevation: 3,
            },
            headerTintColor: '#000',
            headerTitleStyle: {
              fontWeight: '600',
              fontSize: 17,
            },
            headerTitleAlign: 'center',
          })}
        >
          <Tab.Screen 
            name="Summary" 
            component={SummaryFeedScreen} 
            options={{ 
              title: 'BotMR',
              tabBarLabel: 'Summary',
            }}
          />
          <Tab.Screen 
            name="Tasks" 
            component={TasksScreen} 
            options={{ 
              title: 'Tasks',
              tabBarLabel: 'Tasks',
            }}
          />
          
          {/* Central Record Button - Empty placeholder tab */}
          <Tab.Screen
            name="Record"
            component={RecordingScreen}
            options={{
              title: 'Record',
              tabBarLabel: '',
              tabBarIcon: () => null, // Hide default icon since we'll use custom FAB
              tabBarButton: () => null, // This removes the tab button entirely
            }}
          />
          
          <Tab.Screen 
            name="MoM" 
            component={MomScreen} 
            options={{ 
              title: 'Minutes of Meeting',
              tabBarLabel: 'MoM',
            }}
          />
          <Tab.Screen 
            name="Messages" 
            component={MessagesScreen} 
            options={{ 
              title: 'Messages',
              tabBarLabel: 'Messages',
            }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen} 
            options={{ 
              title: 'Settings',
              tabBarLabel: 'Settings',
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}