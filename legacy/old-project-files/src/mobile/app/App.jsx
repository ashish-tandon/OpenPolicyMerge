import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Import screens
import HomeScreen from './screens/HomeScreen';
import PoliciesScreen from './screens/PoliciesScreen';
import RepresentativesScreen from './screens/RepresentativesScreen';
import ParliamentScreen from './screens/ParliamentScreen';
import CivicScreen from './screens/CivicScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Home') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Policies') {
              iconName = focused ? 'shield' : 'shield-outline';
            } else if (route.name === 'Representatives') {
              iconName = focused ? 'people' : 'people-outline';
            } else if (route.name === 'Parliament') {
              iconName = focused ? 'business' : 'business-outline';
            } else if (route.name === 'Civic') {
              iconName = focused ? 'city' : 'city-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#3b82f6',
          tabBarInactiveTintColor: 'gray',
          headerStyle: {
            backgroundColor: '#3b82f6',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        })}
      >
        <Tab.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'OpenPolicy Merge' }}
        />
        <Tab.Screen 
          name="Policies" 
          component={PoliciesScreen} 
          options={{ title: 'Policy Management' }}
        />
        <Tab.Screen 
          name="Representatives" 
          component={RepresentativesScreen} 
          options={{ title: 'Representatives' }}
        />
        <Tab.Screen 
          name="Parliament" 
          component={ParliamentScreen} 
          options={{ title: 'Parliamentary Data' }}
        />
        <Tab.Screen 
          name="Civic" 
          component={CivicScreen} 
          options={{ title: 'Civic Data' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
