var favoriteWord = "mercurial"    // Use your own favorite word!
var favoriteColor = "blue"        // Use your own favorite color!
var favoriteMusician = "Nirvana"

print(favoriteWord)
print(favoriteColor)
print(favoriteMusician)
print("I'm printing a string in Swift!")

let color = "blue"
print("The sky is \(color).")

print("Hi mom, my favorite color is \(favoriteColor) \(favoriteWord) \(favoriteMusician) ")

var ninthPlanet: String

let thirdPlanet: String

let fifthPlanet: String = "Jupiter"
// fifthPlanet is a constant of type ______

// sixthPlanet is a constant of type ______

let seventhPlanet = "Uranus"
// seventhPlanet is a constant of type ______

let sixthPlanet = "Saturn"
let numberOfMoonsOfSaturn = 62

print("\(sixthPlanet) has \(numberOfMoonsOfSaturn) moons.")

func sayHello() {
    let greeting = "hello there"
    print(greeting)
}

var myname = "Anna"

func sayHello(name:String) {
    print("hello \(name)")
}

sayHello(name: myname)

func averageIsAbove75(a: Double, b: Double, c: Double) -> Bool {
    var avg = (a + b + c)/3.0
    if avg > 75 {
        return true
    }
    else {
        return false
    }
}

print(averageIsAbove75(a: 76, b: 75, c: 71.9))

